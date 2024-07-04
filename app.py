from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
from servoclass import servoclass

app = Flask(__name__)
app.secret_key = 'supersecretkey'

servo = servoclass()

#Example activation of servo
servo.SetServoAngle(-1)
servo.StopServoTorque(0)

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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)