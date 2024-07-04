from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
import json
from servoclass import servoclass

app = Flask(__name__)
app.secret_key = 'supersecretkey'

servo = servoclass()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/set_servo_angle', methods=['POST'])
def set_servo_angle():
    data = request.get_json()
    angle = data.get('angle')
    servo.SetServoAngle(angle)
    return jsonify({"status": "success", "angle": angle})

@app.route('/set_get_food_angle', methods=['POST'])
def set_get_food_angle():
    data = request.get_json()
    angle = data.get('angle')
    update_config('get_food_angle', angle)
    return jsonify({"status": "success", "angle": angle})

@app.route('/set_dispense_food_angle', methods=['POST'])
def set_dispense_food_angle():
    data = request.get_json()
    angle = data.get('angle')
    update_config('dispense_food_angle', angle)
    return jsonify({"status": "success", "angle": angle})

def update_config(key, value):
    with open('config.json', 'r') as f:
        config = json.load(f)
    config[key] = value
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)