import json
import time
from servoclass import servoclass

class dispenserclass():
    def __init__(self, config_path='config.json') -> None:
        self.servo = servoclass()

        # Load configuration from JSON file
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.get_food_angle = config.get('get_food_angle', 1)
            self.dispense_food_angle = config.get('dispense_food_angle', -0.92)

    def dispense_food(self):
        for _ in range(45):
            self.servo.SetServoAngle(self.get_food_angle)
            time.sleep(1.6)
            self.servo.SetServoAngle(self.dispense_food_angle)
            time.sleep(1.6)
        
        self.servo.StopServoTorque()

    def dispense_treat(self):
        self.servo.SetServoAngle(self.get_food_angle)
        time.sleep(1.6)
        self.servo.SetServoAngle(self.dispense_food_angle)
        time.sleep(1.6)
        
        self.servo.StopServoTorque()