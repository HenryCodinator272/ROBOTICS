try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

Motor1_PWM_Pin = 11
Motor1_Dir_Pin = 13
Motor2_PWM_Pin = 16
Motor2_Dir_Pin = 18

GPIO.setup(Motor1_Dir_Pin, GPIO.OUT)
GPIO.setup(Motor1_PWM_Pin, GPIO.OUT)

GPIO.setup(Motor2_Dir_Pin, GPIO.OUT)
GPIO.setup(Motor2_PWM_Pin, GPIO.OUT)

motor1Speed = GPIO.PWM(Motor1_PWM_Pin, 1000) #1000 is the frequency
motor2Speed = GPIO.PWM(Motor2_PWM_Pin, 1000)
motor1Speed.start(0)
motor2Speed.start(0)

def check_speed(speed):
    if not 0 <= speed <= 100:
        raise ValueError('Speed must be between 0 and 100')

def check_radius(radius):
    if radius < 0:
        raise ValueError('Only accepts non-negative Radius')

def forward(speed):
    check_speed(speed)
    print(f'Going forward at {speed} speed')
    GPIO.output(Motor1_Dir_Pin, True)
    GPIO.output(Motor2_Dir_Pin, True)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def backward(speed):
    check_speed(speed)
    print(f'Going backward at {speed} speed')
    GPIO.output(Motor1_Dir_Pin, False)
    GPIO.output(Motor2_Dir_Pin, False)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def left_forward(speed, r = 0, diff = 144): #diff --> distance_between_wheels ... r --> radius
    check_speed(speed)
    check_radius(r)
    GPIO.output(Motor1_Dir_Pin, True)
    GPIO.output(Motor2_Dir_Pin, True)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def left_backward(speed, r = 0, diff = 144):
    check_speed(speed)
    check_radius(r)
    GPIO.output(Motor1_Dir_Pin, False)
    GPIO.output(Motor2_Dir_Pin, False)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def right_forward(speed, r=0, diff=144):  # diff --> distance_between_wheels ... r --> radius
    check_speed(speed)
    check_radius(r)
    GPIO.output(Motor1_Dir_Pin, True)
    GPIO.output(Motor2_Dir_Pin, True)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def right_backward(speed, r=0, diff=144):
    check_speed(speed)
    check_radius(r)
    GPIO.output(Motor1_Dir_Pin, False)
    GPIO.output(Motor2_Dir_Pin, False)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def scan(speed):
    check_speed(speed)
    print(f'Scanning at {speed} speed')
    GPIO.output(Motor1_Dir_Pin, True)
    GPIO.output(Motor2_Dir_Pin, False)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def stop():
    GPIO.output(Motor1_Dir_Pin, False)
    GPIO.output(Motor2_Dir_Pin, False)

    motor1Speed.ChangeDutyCycle(0)
    motor2Speed.ChangeDutyCycle(0)

    time.sleep(0.02)
    print('Stopped')


if __name__ == '__main__':
    try:
        forward(10)
        time.sleep(2)
        stop()
    finally:
        motor1Speed.stop()
        motor2Speed.stop()
        GPIO.cleanup()





