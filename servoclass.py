from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

class servoclass:
    def __init__(self):
        max_retries = 5
        for _ in range(max_retries):
            try:
                self.servo = AngularServo(
                    18,
                    initial_angle=0,
                    min_angle=-1,
                    max_angle=1,
                    min_pulse_width=0.001,
                    max_pulse_width=0.002,
                    pin_factory=PiGPIOFactory(host='localhost', port=8888),
                )
                break
            except OSError:
                print(
                    f"Failed to connect to pigpiod. Attempt {_ + 1}/{max_retries}. Retrying in 5 seconds..."
                )
                time.sleep(5)
        else:
            raise RuntimeError("Failed to connect to pigpiod after multiple attempts.")
        self.StopServoTorque()
        self.StopServoTorque()

    def SetServoAngle(self, ServoAngle):
        self.servo.angle = ServoAngle

    def StopServoTorque(self):
        self.servo.value = None