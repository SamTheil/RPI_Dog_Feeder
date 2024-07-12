from flask import Flask, render_template, request, jsonify
import os
import time
import json
from threading import Thread
from dispenserclass import dispenserclass
from MDNSConfigurator import MdnsConfigurator
from GitHubUpdater import GitHubUpdater
import socket
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from math import ceil

time.sleep(5)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

dispenser = dispenserclass()
mdnsconfigurator = MdnsConfigurator()
servo_angle = 0

# Paths to data files
template_path = 'data_template.json'
data_path = 'data.json'

if not os.path.exists(data_path):
    with open(template_path, 'r') as template_file:
        data = json.load(template_file)
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

def read_data():
    with open(data_path, 'r') as data_file:
        return json.load(data_file)

def write_data(data):
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)
    print(f"Data written to {data_path}: {data}")

data = read_data()
get_food_angle = data['food_retrieve_angle']
dispense_food_angle = data['food_dispense_angle']

updater = GitHubUpdater(os.path.dirname(os.path.abspath(__file__)))

scheduler = BackgroundScheduler()
scheduler.start()

def format_recent_meal_message(swipes, meal_type="food"):
    now = datetime.now()
    time_str = now.strftime('%I:%M %p').lstrip('0')

    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    if now >= today:
        day_str = "today"
    elif now >= yesterday:
        day_str = "yesterday"
    else:
        day_str = now.strftime('%A')

    if meal_type == "food":
        return f"{swipes} swipes dispensed at {time_str} {day_str}"
    elif meal_type == "treat":
        return f"Treat dispensed at {time_str} {day_str}"

def update_recent_meal(swipes, meal_type="food"):
    data = read_data()
    data['recent_meal'] = format_recent_meal_message(swipes, meal_type)
    write_data(data)

def schedule_meals():
    data = read_data()
    meals = data.get('meals', [])
    swipe_count = data.get('swipe_count', 10)  # Default to 10 if not set
    scheduler.remove_all_jobs()
    for meal in meals:
        meal_time = datetime.strptime(meal['mealTime'], '%H:%M')
        quantity = float(meal.get('mealQuantity', 1))  # Allow float values
        swipes = round(swipe_count * quantity)  # Round the swipes
        scheduler.add_job(
            lambda swipes=swipes: (dispenser.dispense_food(swipes, get_food_angle, dispense_food_angle), update_recent_meal(swipes)),
            'cron', 
            hour=meal_time.hour, 
            minute=meal_time.minute, 
            id=f"{meal['mealName']}-{meal['mealTime']}"
        )

@app.route('/')
def home():
    data = read_data()
    meals = data.get('meals', [])
    recent_meal = data.get('recent_meal', 'No meal dispensed yet.')
    return render_template('index.html', meals=meals, recent_meal=recent_meal)

@app.route('/wifi')
def wifi_settings():
    return render_template('wifi.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/change_wifi', methods=['POST'])
def change_wifi():
    ssid = request.json['ssid']
    password = request.json['password']
    
    wpa_supplicant_conf = f"""
    country=US
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """

    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        f.write(wpa_supplicant_conf)

    return jsonify({'status': 'success', 'message': 'WiFi settings have been changed.'})

def delayed_reboot():
    time.sleep(5)
    os.system('sudo reboot')

@app.route('/reboot_now', methods=['POST'])
def reboot_now():
    reboot_thread = Thread(target=delayed_reboot)
    reboot_thread.start()
    return jsonify({'message': 'Rebooting now...'})

@app.route('/reboot_later', methods=['POST'])
def reboot_later():
    return jsonify({'message': 'Reboot postponed. Please reboot manually later.'})

@app.route('/start_servo_calibration', methods=['POST'])
def start_servo_calibration():
    global servo_angle
    servo_angle = 0
    dispenser.servo.SetServoAngle(servo_angle)
    return jsonify({'angle': servo_angle})

@app.route('/update_servo_angle', methods=['POST'])
def update_servo_angle():
    global servo_angle
    direction = request.json.get('direction')
    if direction == 'up':
        servo_angle += 0.02
    elif direction == 'down':
        servo_angle -= 0.02
    dispenser.servo.SetServoAngle(servo_angle)
    return jsonify({'angle': servo_angle})

@app.route('/set_food_dispense_angle', methods=['POST'])
def set_food_dispense_angle():
    global servo_angle
    data = read_data()
    data['food_dispense_angle'] = dispenser.servo.GetServoAngle()
    write_data(data)
    return jsonify({'message': 'Food dispense angle set successfully', 'angle': dispenser.servo.GetServoAngle()})

@app.route('/set_food_retrieve_angle', methods=['POST'])
def set_food_retrieve_angle():
    global servo_angle
    data = read_data()
    data['food_retrieve_angle'] = dispenser.servo.GetServoAngle()
    write_data(data)
    return jsonify({'message': 'Food retrieve angle set successfully', 'angle': dispenser.servo.GetServoAngle()})

@app.route('/test_servo_range', methods=['POST'])
def test_servo_range():
    data = read_data()
    retrieve_angle = data.get('food_retrieve_angle', 0)
    dispense_angle = data.get('food_dispense_angle', 1)
    dispenser.servo.SetServoAngle(retrieve_angle)
    time.sleep(1.5)
    dispenser.servo.SetServoAngle(dispense_angle)
    time.sleep(1.5)
    dispenser.servo.SetServoAngle(retrieve_angle)
    return jsonify({'message': 'Servo range test completed'})

@app.route('/dispense_treat', methods=['POST'])
def dispense_treat():
    print("Dispense treat endpoint called")
    dispenser.dispense_treat(get_food_angle, dispense_food_angle)
    data = read_data()
    data['recent_meal'] = format_recent_meal_message(0, "treat")
    write_data(data)
    return jsonify({'message': 'Treat dispensed'})

@app.route('/change_mdns', methods=['POST'])
def change_mdns():
    new_hostname = request.json['hostname']
    mdnsconfigurator.set_hostname(new_hostname)
    return jsonify({'message': 'mDNS configuration updated successfully'})

@app.route('/check_updates', methods=['GET'])
def check_updates():
    result = updater.check_for_updates()
    return jsonify(result)

@app.route('/update_now', methods=['POST'])
def update_now():
    result = updater.update_repo()
    if result["status"] == "updated":
        updater.reboot_device()
    return jsonify(result)

@app.route('/get_current_hostname', methods=['GET'])
def get_current_hostname():
    current_hostname = socket.gethostname()
    return jsonify({'hostname': current_hostname})

@app.route('/update_meal_schedule', methods=['POST'])
def update_meal_schedule():
    meals = request.json['meals']
    data = read_data()
    data['meals'] = meals
    write_data(data)
    schedule_meals()
    return jsonify({'status': 'success', 'message': 'Meal schedule updated successfully'})

@app.route('/finish_calibration', methods=['POST'])
def finish_calibration():
    try:
        # Log the received data
        total_swipes = request.json.get('totalSwipes')
        quantity_in_cups = request.json.get('quantityInCups')
        print(f"Received totalSwipes: {total_swipes}, quantityInCups: {quantity_in_cups}")

        # Ensure the received data is valid
        if total_swipes is None or quantity_in_cups is None:
            return jsonify({'message': 'Invalid data received'}), 400

        # Update the JSON data
        data = read_data()
        data['swipe_count'] = total_swipes / quantity_in_cups
        write_data(data)
        
        return jsonify({'message': 'Calibration completed successfully'})
    except Exception as e:
        print(f"Error in finish_calibration: {e}")
        return jsonify({'message': 'Error during calibration'}), 500

@app.route('/dispense_food', methods=['POST'])
def dispense_food():
    # Check if the request has the required data
    if not request.json or 'swipes' not in request.json:
        print("Invalid request, 'swipes' not in request.json")
        return jsonify({'message': 'Invalid request, swipes parameter missing'}), 400

    swipes = request.json.get('swipes')
    print(f"Dispense food endpoint call with {swipes} swipes")

    # Dispense food
    try:
        dispenser.dispense_food(swipes, get_food_angle, dispense_food_angle)
    except Exception as e:
        print(f"Error dispensing food: {e}")
        return jsonify({'message': 'Error dispensing food'}), 500

    # Read the data from the file and update it
    try:
        data = read_data()
        print(f"Data read from file: {data}")

        # Update the recent meal entry
        data['recent_meal'] = format_recent_meal_message(swipes, "food")
        print(f"Updated data: {data}")

        # Write the updated data back to the file
        write_data(data)
        print(f"Data after writing to file: {data}")
    except Exception as e:
        print(f"Error updating data file: {e}")
        return jsonify({'message': 'Error updating data file'}), 500

    return jsonify({'message': f'Dispensed {swipes} swipes of food'})

if __name__ == '__main__':
    dispenser.servo.SetServoAngle(get_food_angle)
    time.sleep(1.5)
    dispenser.servo.StopServoTorque()

    schedule_meals()
    app.run(host='0.0.0.0', port=80)