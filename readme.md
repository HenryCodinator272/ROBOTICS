# Water Bottle Detector — Pi 5 + Camera Module 3

Three-step pipeline: capture data on the Pi -> train on your laptop/PC ->
deploy the compact model back onto the Pi for real-time detection.

## 1. Capture training photos (on the Pi)

```bash
sudo apt install -y python3-picamera2 python3-opencv
python3 1_capture_data.py --label bottle
python3 1_capture_data.py --label not_bottle
```
Press SPACE to snap a photo, `q` to stop. Get 100-150+ images per class,
varying angle, distance, lighting, and background. The `not_bottle` class
matters as much as the `bottle` class — include your driveway, grass, mail
box, other random objects, etc. so the model actually learns "bottle" and
not just "anything outdoors."

## 2. Train the model (on your laptop/PC, or Google Colab)

Copy the `dataset/` folder off the Pi:
```bash
scp -r pi@<pi-ip-address>:~/water_bottle_detector/dataset .
```

Install and run:
```bash
pip install tensorflow pillow numpy
python3 2_train_model.py --data_dir dataset --epochs 15
```

This produces `model_out/bottle_classifier_int8.tflite` and
`model_out/labels.txt`. Training itself takes a few minutes on a laptop CPU,
faster with a GPU or on Colab.

## 3. Run detection (on the Pi)

Copy the model back:
```bash
scp model_out/bottle_classifier_int8.tflite model_out/labels.txt pi@<pi-ip-address>:~/water_bottle_detector/
```

One-time Pi setup:
```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv build-essential libatlas-base-dev
pip3 install tflite-runtime --break-system-packages
```

Run it:
```bash
python3 3_detect_pi.py --model bottle_classifier_int8.tflite --labels labels.txt
# or, for the headless robot (no monitor attached):
python3 3_detect_pi.py --model bottle_classifier_int8.tflite --labels labels.txt --headless
```

## Notes / tuning

- **Speed**: at 160x160 input with int8 quantization, expect roughly
  15-40ms inference per frame on the Pi 5's CPU (well over 20 fps) — you
  don't need a Coral accelerator for a single-object classifier like this.
- **Accuracy vs. false positives**: raise `--threshold` (default 0.6) if
  it's flagging bottles that aren't there; lower it if it's missing real
  ones.
- **This is a whole-frame classifier, not a bounding-box detector** — it
  tells you "bottle in view" but not exactly where. That's usually enough
  to drive a robot toward/away from a target using simple heuristics
  (e.g. pan the camera/robot until confidence peaks). If you later need
  exact pixel coordinates, that's a bigger project (SSD/YOLO-style
  detector with bounding-box-labeled data) — worth doing only if the
  1-week deadline allows it.
- **Retraining**: if the robot misses bottles in real conditions (outdoor
  light, driveway background), capture more `not_bottle`/`bottle` images
  in those exact conditions and rerun step 2 — this matters more than
  almost anything else for real-world accuracy.