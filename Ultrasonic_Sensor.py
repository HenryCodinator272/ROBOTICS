import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO

#Channel Numbers instead of Location Number (numbers match on board)
GPIO.setmode(GPIO.BCM)
trigPin = 23
echoPin = 24
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

def run_ping():

    distances = []
    delayTime = 0.05

    for _ in range(5):

        #initializes trig pin at LOW (0 output)
        GPIO.output(trigPin, 0)

        #gives it time to initialize
        time.sleep(2E-6)

        #sets the trig pin to HIGH Voltage for 10 microseconds
        GPIO.output(trigPin, 1)
        time.sleep(10E-6)

        #returns back to low
        GPIO.output(trigPin, 0)

        #creates a reference time for next loop
        ref = time.time()

        while GPIO.input(echoPin) == 0:
            #if it's still running after 0.03 seconds, there's an issue
            if time.time() > ref + 0.03:
                break
        else:
            #echo pin should turn on once the pulse is sent out
            #it will stay high until it receives the return pulse
            echoStartTime = time.time()
            while GPIO.input(echoPin) == 1:
                #if it takes longer than 0.03 seconds to receive, something is wrong
                if time.time() > echoStartTime + 0.03:
                    break
            else:

                #once it returns to LOW output
                echoStopTime = time.time()

                #Calculations
                delta_Time = echoStopTime - echoStartTime
                speed_sound_meters = 343
                speed_sound_cm = 100 * speed_sound_meters
                distance_cm = speed_sound_cm * delta_Time / 2
                distances.append(distance_cm)

                #time to rest
                time.sleep(delayTime)

    distances.sort()
    return distances[len(distances) // 2]

