from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import time
import json
from servoclass import servoclass

time.sleep(5)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

servo = servoclass()
servo_angle = 0

# Paths to data files
template_path = 'data_template.json'
data_path = 'data.json'

# Copy template to data.json if it doesn't exist
if not os.path.exists(data_path):
    with open(template_path, 'r') as template_file:
        data = json.load(template_file)
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

# Function to read data
def read_data():
    with open(data_path, 'r') as data_file:
        return json.load(data_file)

# Function to write data
def write_data(data):
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

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
    ssid = request.form['ssid']
    password = request.form['password']
    
    # Create a wpa_supplicant.conf content
    wpa_supplicant_conf = f"""
    country=US
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """

    # Write the new configuration to wpa_supplicant.conf
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        f.write(wpa_supplicant_conf)

    # Restart the WiFi interface
    os.system('sudo wpa_cli -i wlan0 reconfigure')

    flash('WiFi settings have been changed. Device will reboot now.')

    time.sleep(1)

    os.system('sudo reboot')

    return redirect(url_for('home'))

@app.route('/start_servo_calibration', methods=['POST'])
def start_servo_calibration():
    global servo_angle
    servo_angle = 0
    servo.SetServoAngle(servo_angle)
    return jsonify({'angle': servo_angle})

@app.route('/update_servo_angle', methods=['POST'])
def update_servo_angle():
    global servo_angle
    direction = request.json.get('direction')
    if direction == 'up':
        servo_angle += 0.02
    elif direction == 'down':
        servo_angle -= 0.02
    servo.SetServoAngle(servo_angle)
    return jsonify({'angle': servo_angle})

@app.route('/set_food_dispense_angle', methods=['POST'])
def set_food_dispense_angle():
    global servo_angle
    data = read_data()
    data['food_dispense_angle'] = servo.GetServoAngle()
    write_data(data)
    return jsonify({'message': 'Food dispense angle set successfully', 'angle': servo.GetServoAngle()})

@app.route('/set_food_retrieve_angle', methods=['POST'])
def set_food_retrieve_angle():
    global servo_angle
    data = read_data()
    data['food_retrieve_angle'] = servo.GetServoAngle()
    write_data(data)
    return jsonify({'message': 'Food retrieve angle set successfully', 'angle': servo.GetServoAngle()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)