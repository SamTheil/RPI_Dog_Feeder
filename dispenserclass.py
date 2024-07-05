from servoclass import servoclass
import time

class dispenserclass():
  def __init__(self) -> None:
    self.servo = servoclass()

  def dispense_food(self, number_swipes, get_food_angle, dispense_food_angle):
    for _ in range(number_swipes):
      self.servo.SetServoAngle(get_food_angle)
      time.sleep(1.6)
      self.servo.SetServoAngle(dispense_food_angle)
      time.sleep(1.6)
    
    self.servo.StopServoTorque()

  def dispense_treat(self, get_food_angle, dispense_food_angle):
    self.servo.SetServoAngle(get_food_angle)
    time.sleep(1.6)
    self.servo.SetServoAngle(dispense_food_angle)
    time.sleep(1.6)
  
    self.servo.StopServoTorque()