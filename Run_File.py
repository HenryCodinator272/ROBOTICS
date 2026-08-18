from picamera2 import Picamera2
import cv2
import time
import torch
import training
import os
from torchvision import transforms
from model import Bottle_Detection_Model
from PIL import Image


def main():
    #initialization
    motor_active = False
    picam2 = Picamera2()
    config = picam2.create_video_configuration() #picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    model = Bottle_Detection_Model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transform = transforms.Compose([transforms.Resize((224, 224)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    if os.path.exists('best_bottle_model.pth'):
        weights = torch.load('best_bottle_model.pth', map_location = device, weights_only=True)
        model.load_state_dict(weights)
        model.to(device)
        model.eval()
    else:
        return 'No Weight Dictionary to Load:\nPlease Accumulate More Training Data.'

    #loop
    try:
        while True:

            ### BOTTLE DETECTION ###

            bottle_detected = False
            frame = picam2.capture_array()
            f_height, f_width, _ = frame.shape
            img = frame[:, :, ::-1]
            img = Image.fromarray(img)
            tensor = transform(img).to(device).unsqueeze(0)
            with torch.no_grad():
                out = model(tensor)
            vals = training.create_box(out.squeeze(0))
            if vals:
                x1, x2, y1, y2, w, h = vals
                bottle_detected = True

                x1_scaled = int(x1 / 224 * f_width)
                x2_scaled = int(x2 / 224 * f_width)
                y1_scaled = int(y1 / 224 * f_height)
                y2_scaled = int(y2 / 224 * f_height)

                cv2.rectangle(frame, (x1_scaled, y1_scaled),
                              (x2_scaled, y2_scaled), (0, 255, 0), 2)

            cv2.imshow('Live Bottle Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


            ### MOVEMENT LOGIC ###
            if bottle_detected:
                x_center = (x1_scaled + x2_scaled) // 2 - f_width
                y_center = (y1_scaled + y2_scaled) // 2 - f_height
                width = int(w / 224 * f_width)
                height = int(h / 224 * f_height)

                if x_center < 0:
                    if abs(x_center) > f_width / 4:
                        pass #big left turn
                    else:
                        pass #small left turn
                else:
                    if abs(x_center) > f_width / 4:
                        pass #big right turn
                    else:
                        pass #small right turn


    finally:
        cv2.destroyAllWindows()
        picam2.stop()
