from flask import Flask, render_template, request, jsonify
import os
import time
import json
from threading import Thread
from dispenserclass import dispenserclass
from MDNSConfigurator import MdnsConfigurator

class GitHubUpdater:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.configure_safe_directory()

    def configure_safe_directory(self):
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", self.repo_dir])

    def check_for_updates(self):
        os.chdir(self.repo_dir)
        result = subprocess.run(["git", "fetch"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        if "Your branch is up to date" in result.stdout:
            return {"status": "up-to-date"}
        else:
            return {"status": "update-available"}

    def update_repo(self):
        os.chdir(self.repo_dir)
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        return {"status": "updated", "message": result.stdout}
    
    def reboot_device(self):
        subprocess.run(["sudo", "reboot"])

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

data = read_data()
get_food_angle = data['food_retrieve_angle']
dispense_food_angle = data['food_dispense_angle']

updater = GitHubUpdater(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def home():
    return render_template('index.html')

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
    dispenser.dispense_treat(get_food_angle, dispense_food_angle)

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

if __name__ == '__main__':
    dispenser.servo.SetServoAngle(get_food_angle)
    time.sleep(1.5)
    dispenser.servo.StopServoTorque()

    app.run(host='0.0.0.0', port=80)
