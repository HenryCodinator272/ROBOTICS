try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO
import time
import numpy as np

GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

motor1Speed = GPIO.PWM(17, 1000) #1000 is the frequency
motor2Speed = GPIO.PWM(19, 1000)
motor1Speed.start(0)
motor2Speed.start(0)

def forward(speed):
    print(f'Going forward at {speed} speed')
    GPIO.output(16, True)
    GPIO.output(18, True)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def backward(speed):
    print(f'Going backward at {speed} speed')
    GPIO.output(16, False)
    GPIO.output(18, False)

    motor1Speed.ChangeDutyCycle(speed)
    motor2Speed.ChangeDutyCycle(speed)

def left_forward(speed, r = 0, diff = 160): #diff --> distance_between_wheels ... r --> radius
    GPIO.output(16, True)
    GPIO.output(18, True)

    inner_wheel_speed = r * speed / (r + diff / 2)
    outer_wheel_speed = (r+diff)*speed/(r+diff/2)

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def left_backward(speed, r = 0, diff = 160):
    GPIO.output(16, False)
    GPIO.output(18, False)

    inner_wheel_speed = r * speed / (r + diff / 2)
    outer_wheel_speed = (r + diff) * speed / (r + diff / 2)

    motor1Speed.ChangeDutyCycle(inner_wheel_speed)
    motor2Speed.ChangeDutyCycle(outer_wheel_speed)

def right_forward(speed, r=0, diff=160):  # diff --> distance_between_wheels ... r --> radius
    GPIO.output(16, True)
    GPIO.output(18, True)

    inner_wheel_speed = r * speed / (r + diff / 2)
    outer_wheel_speed = (r + diff) * speed / (r + diff / 2)

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def right_backward(speed, r=0, diff=160):
    GPIO.output(16, False)
    GPIO.output(18, False)

    inner_wheel_speed = r * speed / (r + diff / 2)
    outer_wheel_speed = (r + diff) * speed / (r + diff / 2)

    motor1Speed.ChangeDutyCycle(outer_wheel_speed)
    motor2Speed.ChangeDutyCycle(inner_wheel_speed)

def stop():
    GPIO.output(16, False)
    GPIO.output(18, False)

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




