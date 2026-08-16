"""
3_detect_pi.py
Run this ON THE RASPBERRY PI 5 with the Camera Module 3.

Loads the trained .tflite model and runs live detection off the camera
feed, printing/displaying whether a water bottle is in view.

One-time setup on the Pi (Raspberry Pi OS Bookworm, 64-bit):
    sudo apt update
    sudo apt install -y python3-picamera2 python3-opencv build-essential libatlas-base-dev
    pip3 install tflite-runtime --break-system-packages

Copy these onto the Pi (e.g. via scp) before running:
    model_out/bottle_classifier_int8.tflite   (or the fp16 fallback)
    model_out/labels.txt

Usage:
    python3 3_detect_pi.py --model bottle_classifier_int8.tflite --labels labels.txt

Press 'q' to quit the preview window. If you don't have a display attached
(headless robot), use --headless to just print detections to the terminal.
"""

import argparse
import time

import cv2
import numpy as np
from picamera2 import Picamera2

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    # fall back to full tensorflow if tflite_runtime isn't installed
    import tensorflow.lite as tflite


def load_labels(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="bottle_classifier_int8.tflite")
    parser.add_argument("--labels", default="labels.txt")
    parser.add_argument("--threshold", type=float, default=0.6,
                         help="Confidence threshold to report 'bottle detected'")
    parser.add_argument("--headless", action="store_true",
                         help="No display -- just print results (use this for the robot)")
    args = parser.parse_args()

    labels = load_labels(args.labels)  # ["not_bottle", "bottle"]

    interpreter = tflite.Interpreter(model_path=args.model, num_threads=4)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    img_size = input_details["shape"][1]  # e.g. 160
    is_quantized = input_details["dtype"] == np.uint8

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(1)

    print("Running. Ctrl+C or 'q' to stop.")
    try:
        while True:
            frame = picam2.capture_array()  # RGB888, 640x480

            resized = cv2.resize(frame, (img_size, img_size))
            input_data = np.expand_dims(resized, axis=0)
            if not is_quantized:
                input_data = input_data.astype(np.float32) / 255.0
            else:
                input_data = input_data.astype(np.uint8)

            t0 = time.time()
            interpreter.set_tensor(input_details["index"], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details["index"])[0]
            inference_ms = (time.time() - t0) * 1000

            # sigmoid output: dequantize if needed
            if is_quantized:
                scale, zero_point = output_details["quantization"]
                score = (output[0].astype(np.float32) - zero_point) * scale
            else:
                score = float(output[0])

            bottle_detected = score >= args.threshold
            label = "BOTTLE" if bottle_detected else "no bottle"

            if args.headless:
                print(f"{label}  score={score:.2f}  ({inference_ms:.0f} ms)")
            else:
                color = (0, 255, 0) if bottle_detected else (0, 0, 255)
                display = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.putText(display, f"{label} ({score:.2f})  {inference_ms:.0f}ms",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.imshow("bottle detector", display)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            # --- hook point ---
            # This is where you'd trigger robot behavior, e.g.:
            # if bottle_detected:
            #     drive_toward_target()

    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        if not args.headless:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()