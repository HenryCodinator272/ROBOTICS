from picamera2 import Picamera2
import cv2
import time
import torch
import training
import os
import RPi.GPIO as GPIO
from torchvision import transforms
from model import Bottle_Detection_Model
from PIL import Image
import motor_driver
import ultrasonic_sensor

def main():
    #initialization
    motor_active = False
    blind_scan_end_time = 0.0
    c = 0

    lf = False
    rf = False
    b = False
    f = False
    scan = False

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
        picam2.stop()
        GPIO.cleanup()
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

                x1_scaled = int(x1 / 224 * f_width)
                x2_scaled = int(x2 / 224 * f_width)
                y1_scaled = int(y1 / 224 * f_height)
                y2_scaled = int(y2 / 224 * f_height)

                bottle_detected = True

                cv2.rectangle(frame, (x1_scaled, y1_scaled),
                              (x2_scaled, y2_scaled), (0, 255, 0), 2)

            cv2.imshow('Live Bottle Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if c == 0:
                if time.time() > blind_scan_end_time:
                    ping = ultrasonic_sensor.run_ping()
                    print(f'PING: {ping} cm')
                    if ping < 20:
                        print("TOO CLOSE! Initiating 1 second escape spin")
                        if not scan:

                            lf = False
                            rf = False
                            b = False
                            f = False
                            scan = True

                            if motor_active:
                                motor_driver.stop()
                            motor_active = True
                            motor_driver.scan(10)
                            blind_scan_end_time = time.time() + 1.0
                        continue
                else:
                    continue
                c = 20
            else:
                c -= 1

            ### MOVEMENT LOGIC ###

            if bottle_detected:

                x_center = (x1_scaled + x2_scaled) // 2 - f_width // 2
                y_center = (y1_scaled + y2_scaled) // 2 - f_height // 2
                width = int(w / 224 * f_width)
                height = int(h / 224 * f_height)
                #far = True if height > f_height / 2 else False

                if x_center < -20 and lf == False:

                    lf = True
                    rf = False
                    b = False
                    f = False
                    scan = False

                    if motor_active:
                        motor_driver.stop()
                    motor_active = True
                    motor_driver.left_forward(40, 20)
                elif x_center > 20 and rf == False:

                    lf = False
                    rf = True
                    b = False
                    f = False
                    scan = False

                    if motor_active:
                        motor_driver.stop()
                    motor_active = True
                    motor_driver.right_forward(40, 20)
                elif -20 <= x_center <= 20 and f == False:

                    lf = False
                    rf = False
                    b = False
                    f = True
                    scan = False

                    if motor_active:
                        motor_driver.stop()
                    motor_active = True
                    motor_driver.forward(40)

            elif not bottle_detected:

                    if not scan:

                        lf = False
                        rf = False
                        b = False
                        f = False
                        scan = True

                        if motor_active:
                            motor_driver.stop()
                        motor_active = True
                        motor_driver.scan(10)



    finally:
        motor_driver.stop()
        GPIO.cleanup()
        cv2.destroyAllWindows()
        picam2.stop()

if __name__ == '__main__':
    main()