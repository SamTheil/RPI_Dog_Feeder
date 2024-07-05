import os
import time
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

def start_pigpiod():
    if os.system('pgrep pigpiod > /dev/null') != 0:
        os.system('sudo pigpiod')

class servoclass:
    def __init__(self):
        self.servo_angle = 0
        start_pigpiod()
        max_retries = 5
        for _ in range(max_retries):
            try:
                print("Attempting to connect to pigpiod...")
                self.servo = AngularServo(
                    18,
                    initial_angle=0,
                    min_angle=-1,
                    max_angle=1,
                    min_pulse_width=0.0005,
                    max_pulse_width=0.0025,
                    pin_factory=PiGPIOFactory(),
                )
                print("Connected to pigpiod.")
                break
            except OSError as e:
                print(f"Failed to connect to pigpiod: {e}")
                print(f"Attempt {_ + 1}/{max_retries}. Retrying in 5 seconds...")
                time.sleep(5)
        else:
            raise RuntimeError("Failed to connect to pigpiod after multiple attempts.")
        self.StopServoTorque()
        self.StopServoTorque()

    def SetServoAngle(self, ServoAngle):
        self.servo.angle = ServoAngle
        self.servo_angle = ServoAngle

    def StopServoTorque(self):
        self.servo.value = None

    def GetServoAngle(self):
        return self.servo_angle