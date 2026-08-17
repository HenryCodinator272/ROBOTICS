from picamera2 import Picamera2, Preview
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
    count = 0 if len(files) == 0 else int(files[-1][-7:-4])

    try:
        while True:
            frame = picam2.capture_array()
            cv2.imshow('Camera', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):
                count += 1
                img = Image.fromarray(frame)
                img.save(os.path.join('Training_Files', f'image_{count:03d}.jpg'))

                tensor = torch.from_numpy(frame)
                torch.save(tensor, os.path.join('Training_Files', f'image_{count:03d}.pt'))
                print(f'\nTotal_Images: {count}\n'
                      f'Press q to quit.\n'
                      f'Press SPACE to generate the next image.\n')

            if key == ord('q'):
                break

    finally:
        picam2.close()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    main()




#create directory
#take photo
#put it in the folder with the correct class
#close camera
#turn everything off

#python data_collection.py --label 0 --size 25 32