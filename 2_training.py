"""
2_train_model.py
Run this on your LAPTOP/DESKTOP (or Google Colab) -- NOT on the Pi.
Training a CNN on the Pi 5's CPU would be very slow; the Pi only needs to
run the finished, converted model.

Expects a folder structure like:
    dataset/
        bottle/
            bottle_0000.jpg
            bottle_0001.jpg
            ...
        not_bottle/
            not_bottle_0000.jpg
            ...

(This is exactly what 1_capture_data.py produces -- just copy the
`dataset/` folder from the Pi over to this machine, e.g. with scp:
    scp -r pi@<pi-ip>:~/water_bottle_detector/dataset .  )

What this does:
    1. Loads images, splits into train/validation
    2. Fine-tunes a MobileNetV2 (pretrained on ImageNet) as a
       binary classifier: bottle vs. not_bottle
    3. Saves a Keras model AND a quantized .tflite file ready for the Pi

Install deps (one time):
    pip install tensorflow pillow numpy

Run:
    python3 2_train_model.py --data_dir dataset --epochs 15
"""

import argparse
import os

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


def build_model(img_size):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # freeze for initial training

    inputs = tf.keras.Input(shape=(img_size, img_size, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)  # 1 = bottle, 0 = not_bottle
    model = models.Model(inputs, outputs)
    return model, base


def representative_dataset_gen(train_ds, img_size):
    def gen():
        for images, _ in train_ds.take(50):
            for i in range(images.shape[0]):
                img = tf.expand_dims(images[i], axis=0)
                yield [tf.cast(img, tf.float32)]

    return gen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="dataset")
    parser.add_argument("--img_size", type=int, default=160,
                        help="Input resolution (160 is a good speed/accuracy "
                             "tradeoff for Pi 5 real-time inference)")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--fine_tune_epochs", type=int, default=5,
                        help="Extra epochs unfreezing top layers of MobileNetV2")
    parser.add_argument("--out_dir", default="model_out")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        args.data_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        label_mode="binary",
        class_names=["not_bottle", "bottle"],  # 0 = not_bottle, 1 = bottle
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        args.data_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        label_mode="binary",
        class_names=["not_bottle", "bottle"],
    )

    # light augmentation to make up for a small dataset
    augment = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomZoom(0.1),
        layers.RandomBrightness(0.15),
    ])
    train_ds = train_ds.map(lambda x, y: (augment(x, training=True), y))

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    model, base = build_model(args.img_size)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    print("\n--- Stage 1: training classifier head (base frozen) ---")
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs)

    print("\n--- Stage 2: fine-tuning top layers of MobileNetV2 ---")
    base.trainable = True
    # only unfreeze the last ~30 layers so we don't overfit / destroy pretrained features
    for layer in base.layers[:-30]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs)

    keras_path = os.path.join(args.out_dir, "bottle_classifier.keras")
    model.save(keras_path)
    print(f"\nSaved Keras model to {keras_path}")

    # ---- Convert to TFLite (int8 quantized for fast Pi 5 CPU inference) ----
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset_gen(train_ds, args.img_size)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    try:
        tflite_model = converter.convert()
        tflite_path = os.path.join(args.out_dir, "bottle_classifier_int8.tflite")
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"Saved quantized TFLite model to {tflite_path}")
    except Exception as e:
        print(f"Full int8 quantization failed ({e}); falling back to float16 model.")
        converter2 = tf.lite.TFLiteConverter.from_keras_model(model)
        converter2.optimizations = [tf.lite.Optimize.DEFAULT]
        converter2.target_spec.supported_types = [tf.float16]
        tflite_model = converter2.convert()
        tflite_path = os.path.join(args.out_dir, "bottle_classifier_fp16.tflite")
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"Saved float16 TFLite model to {tflite_path}")

    with open(os.path.join(args.out_dir, "labels.txt"), "w") as f:
        f.write("not_bottle\nbottle\n")

    print(f"\nDone. Copy the .tflite file and labels.txt from {args.out_dir}/ "
          f"onto the Pi 5, then run 3_detect_pi.py there.")


if __name__ == "__main__":
    main()
