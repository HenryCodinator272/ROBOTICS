"""
1_capture_data.py
Run this ON THE RASPBERRY PI 5 with the Camera Module 3 attached.

Captures labeled training images for the classifier. You'll collect two
classes:
    - bottle       -> water bottle clearly in frame, varied angles/lighting
    - not_bottle   -> empty background, other objects, hands, etc.

Usage:
    python3 1_capture_data.py --label bottle
    python3 1_capture_data.py --label not_bottle

Press SPACE to capture a photo, 'q' to quit.
Aim for at least 100-150 images per class. Vary:
    - distance from camera
    - angle / rotation of the bottle
    - lighting (sun, shade, indoor light)
    - background (this matters a lot for a robot moving around outside)

After capturing, copy the whole `dataset/` folder to your training machine
(laptop/desktop/Colab) for step 2.
"""

import argparse
import os
import time

import cv2
from picamera2 import Picamera2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, choices=["bottle", "not_bottle"],
                         help="Which class you're capturing images for")
    parser.add_argument("--outdir", default="dataset",
                         help="Root folder to save images into")
    parser.add_argument("--size", type=int, nargs=2, default=[640, 480],
                         help="Capture resolution, e.g. --size 640 480")
    args = parser.parse_args()

    save_dir = os.path.join(args.outdir, args.label)
    os.makedirs(save_dir, exist_ok=True)
    existing = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": tuple(args.size)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(1)  # let auto-exposure settle

    print(f"Capturing class '{args.label}' into {save_dir}")
    print(f"Already have {existing} images in this class.")
    print("SPACE = capture, q = quit")

    count = existing
    try:
        while True:
            frame = picam2.capture_array()
            display = frame.copy()
            cv2.putText(display, f"label={args.label}  count={count}  [SPACE]=capture [q]=quit",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("capture", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):
                fname = os.path.join(save_dir, f"{args.label}_{count:04d}.jpg")
                cv2.imwrite(fname, frame)
                count += 1
                print(f"saved {fname}")
            elif key == ord("q"):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

    print(f"Done. {count} total images in {save_dir}")


if __name__ == "__main__":
    main()