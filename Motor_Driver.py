try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)

GPIO.setup(13, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)

motor1Speed = GPIO.PWM(29, 1000) #1000 is the frequency
motor2Speed = GPIO.PWM(31, 1000)
motor1Speed.start(0)
motor2Speed.start(0)

def forward(speed):
    print(f'Going forward at {speed} speed')
    GPIO.output(11, True)
    GPIO.output(13, True)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def backward(speed):
    print(f'Going backward at {speed} speed')
    GPIO.output(11, False)
    GPIO.output(13, False)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def left_forward(speed, r = 0, diff = 144): #diff --> distance_between_wheels ... r --> radius
    GPIO.output(11, True)
    GPIO.output(13, True)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def left_backward(speed, r = 0, diff = 144):
    GPIO.output(11, False)
    GPIO.output(13, False)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def right_forward(speed, r=0, diff=144):  # diff --> distance_between_wheels ... r --> radius
    GPIO.output(11, True)
    GPIO.output(13, True)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def right_backward(speed, r=0, diff=144):
    GPIO.output(11, False)
    GPIO.output(13, False)

    inner_wheel_speed = r * speed / (r + diff)
    outer_wheel_speed = speed

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def stop():
    GPIO.output(11, False)
    GPIO.output(13, False)

    motor1Speed.ChangeDutyCycle(0)
    motor2Speed.ChangeDutyCycle(0)
    print('Stopped')

try:
    forward(10)
    time.sleep(2)
    stop()
finally:
    motor1Speed.stop()
    motor2Speed.stop()
    GPIO.cleanup()




