from picamera2 import Picamera2
import time
import os
import argparse
from PIL import Image
import torch
import cv2

def main():

    os.makedirs('Training_Files', exist_ok = True)

    parser = argparse.ArgumentParser()
    parser.add_argument('--size', nargs = 2, help = 'dimensions of image', default = [1280, 720], type = int)
    args = parser.parse_args()

    picam2 = Picamera2()
    config = picam2.create_still_configuration(main = {'size': tuple(args.size)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    files = sorted(f for f in os.listdir('Training_Files') if f.endswith('.jpg'))
    count = 0 if len(files) == 0 else int(files[-1][-8:-4])
    tracker = 0

    print('DATA COLLECTION: \n'
          'Press SPACE to take a Picture \n'
          'Press q to Quit \n')

    try:
        bottle_added_ratios = 0
        while True:
            frame = picam2.capture_array()
            cv2.imshow('Camera', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):
                answer = None
                while answer not in ['y', 'n']:
                    answer = input('\nIs there a bottle?\n Bottle: y\n No Bottle: n\n')

                if 'y' == answer:
                    x, y, w, h = cv2.selectROI('Camera', frame, fromCenter=False) #x is left edge, y is top edge w is width and h is height
                    if w == 0 or h == 0:
                        print('No Box Selected')
                        continue
                    x = x/args.size[1]
                    y = y/args.size[0]
                    w = w/args.size[1]
                    h = h/args.size[0]
                    x_center, y_center = x + w/2, y+h/2
                    new_tensor = torch.tensor([x_center, y_center, w, h, 1.0], dtype=torch.float32)
                    bottle_pixel_ratio = w*h
                else:
                    bottle_pixel_ratio = 0
                    new_tensor = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0], dtype=torch.float32)

                bottle_added_ratios += bottle_pixel_ratio
                tracker += 1
                count += 1

                img = Image.fromarray(frame)
                img.save(os.path.join('Training_Files', f'image_{count:04d}.jpg'))
                torch.save(new_tensor, os.path.join('Training_Files', f'label_{count:04d}.pt'))
                print(f'\nTotal_Images: {count}\n'
                      f'Press q to quit.\n'
                      f'Press SPACE to generate the next image.\n')

            if key == ord('q'):
                break

    finally:
        if tracker > 0:
            print(f'Bottle Ratio: {bottle_added_ratios/tracker:.2f}')
        picam2.close()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    main()