try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

Motor1_In1 = 11
Motor1_In2 = 13
Motor1_En = 22

Motor2_In1 = 16
Motor2_In2 = 18
Motor2_En = 29

GPIO.setup(Motor1_In1, GPIO.OUT) #PWM for forward
GPIO.setup(Motor1_In2, GPIO.OUT) #PWM for backward
GPIO.setup(Motor1_En, GPIO.OUT) #Enable

GPIO.setup(Motor2_In1, GPIO.OUT) #PWM for forward
GPIO.setup(Motor2_In2, GPIO.OUT) #PWM for backward
GPIO.setup(Motor2_En, GPIO.OUT) #Enable

motor1Speed1 = GPIO.PWM(Motor1_In1, 1000) #1000 is the frequency
motor1Speed2 = GPIO.PWM(Motor1_In2, 1000)

motor2Speed1 = GPIO.PWM(Motor2_In1, 1000)
motor2Speed2 = GPIO.PWM(Motor2_In2, 1000)

motor1Speed1.start(0)
motor1Speed2.start(0)
motor2Speed1.start(0)
motor2Speed2.start(0)

GPIO.output(Motor1_En, GPIO.HIGH)
GPIO.output(Motor2_En, GPIO.HIGH)

def check_speed(speed):
    if not 0 <= speed <= 100:
        raise ValueError('Speed must be between 0 and 100')

def check_radius(radius):
    if radius < 0:
        raise ValueError('Only accepts non-negative Radius')

def forward(speed):
    check_speed(speed)
    print(f'Going forward at {speed} speed')

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(speed)

    motor2Speed2.ChangeDutyCycle(0)
    motor2Speed1.ChangeDutyCycle(speed)

def backward(speed):
    check_speed(speed)
    print(f'Going backward at {speed} speed')

    motor1Speed1.ChangeDutyCycle(0)
    motor1Speed2.ChangeDutyCycle(speed)

    motor2Speed1.ChangeDutyCycle(0)
    motor2Speed2.ChangeDutyCycle(speed)

def left_forward(speed, r = 0, diff = 144): #diff --> distance_between_wheels ... r --> radius
    check_speed(speed)
    check_radius(r)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(inner_wheel_speed)

    motor2Speed2.ChangeDutyCycle(0)
    motor2Speed1.ChangeDutyCycle(outer_wheel_speed)

def left_backward(speed, r = 0, diff = 144):
    check_speed(speed)
    check_radius(r)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed1.ChangeDutyCycle(0)
    motor1Speed2.ChangeDutyCycle(inner_wheel_speed)

    motor2Speed1.ChangeDutyCycle(0)
    motor2Speed2.ChangeDutyCycle(outer_wheel_speed)

def right_forward(speed, r=0, diff=144):  # diff --> distance_between_wheels ... r --> radius
    check_speed(speed)
    check_radius(r)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(outer_wheel_speed)

    motor2Speed2.ChangeDutyCycle(0)
    motor2Speed1.ChangeDutyCycle(inner_wheel_speed)

def right_backward(speed, r=0, diff=144):
    check_speed(speed)
    check_radius(r)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed1.ChangeDutyCycle(0)
    motor1Speed2.ChangeDutyCycle(outer_wheel_speed)

    motor2Speed1.ChangeDutyCycle(0)
    motor2Speed2.ChangeDutyCycle(inner_wheel_speed)

def scan(speed):
    check_speed(speed)
    print(f'Scanning at {speed} speed')

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(speed)

    motor2Speed1.ChangeDutyCycle(0)
    motor2Speed2.ChangeDutyCycle(speed)

def stop():

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(0)

    motor2Speed2.ChangeDutyCycle(0)
    motor2Speed1.ChangeDutyCycle(0)

    time.sleep(0.02)
    print('Stopped')

def brake():
    print('Braking...')

    motor1Speed2.ChangeDutyCycle(100)
    motor1Speed1.ChangeDutyCycle(100)
    motor2Speed1.ChangeDutyCycle(100)
    motor2Speed2.ChangeDutyCycle(100)

    motor1Speed2.ChangeDutyCycle(0)
    motor1Speed1.ChangeDutyCycle(0)
    motor2Speed1.ChangeDutyCycle(0)
    motor2Speed2.ChangeDutyCycle(0)

    time.sleep(0.1)
    stop()

if __name__ == '__main__':
    try:
        forward(10)
        time.sleep(2)
        brake()
    finally:
        motor1Speed1.stop()
        motor1Speed2.stop()
        motor2Speed1.stop()
        motor2Speed2.stop()
        GPIO.cleanup()





