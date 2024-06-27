#!/bin/bash

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Please run with sudo."
    exit 1
fi

# Set hostname
echo "Setting hostname to 'feeder'..."
echo "feeder" > /etc/hostname

# Update /etc/hosts
echo "Updating /etc/hosts..."
sed -i '/127.0.1.1/d' /etc/hosts
echo "127.0.0.1       localhost" > /etc/hosts
echo "127.0.1.1       feeder" >> /etc/hosts

# Apply hostname changes
echo "Applying hostname changes..."
hostnamectl set-hostname feeder
systemctl restart systemd-hostnamed

# Install avahi-daemon
echo "Installing avahi-daemon..."
apt-get update
apt-get install -y avahi-daemon avahi-utils

# Configure avahi-daemon
echo "Configuring avahi-daemon..."
AVAHI_CONF="/etc/avahi/avahi-daemon.conf"
if grep -q "host-name=" "$AVAHI_CONF"; then
    sed -i 's/^host-name=.*/host-name=feeder/' "$AVAHI_CONF"
else
    sed -i '/\[server\]/a host-name=feeder' "$AVAHI_CONF"
fi

# Restart avahi-daemon
echo "Restarting avahi-daemon..."
systemctl restart avahi-daemon

# Check avahi-daemon status
systemctl status avahi-daemon --no-pager

# Install required packages
echo "Installing required packages..."
apt-get install -y python3-flask python3-git python3-requests hostapd dnsmasq network-manager

# Create hostapd configuration
echo "Creating hostapd configuration..."
cat <<EOT > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=dogfeeder
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=password
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOT

echo "Updating hostapd defaults..."
sed -i 's|#DAEMON_CONF="|"DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Create dnsmasq configuration
echo "Creating dnsmasq configuration..."
cat <<EOT > /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOT

# Set static IP for wlan0
echo "Configuring static IP for wlan0..."
cat <<EOT >> /etc/dhcpcd.conf
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOT

# Create the wifi_manager.py script
echo "Creating wifi_manager.py script..."
cat <<EOT > /home/pizero/Dog_Feeder_V2/wifi_manager.py
import os
import time

def check_wifi_connection():
    result = os.system("ping -c 1 google.com > /dev/null 2>&1")
    return result == 0

def start_access_point():
    os.system("sudo systemctl stop NetworkManager")
    os.system("sudo systemctl start hostapd")
    os.system("sudo systemctl start dnsmasq")

def stop_access_point():
    os.system("sudo systemctl stop hostapd")
    os.system("sudo systemctl stop dnsmasq")
    os.system("sudo systemctl start NetworkManager")

def main():
    while True:
        if check_wifi_connection():
            print("Connected to WiFi.")
            stop_access_point()
        else:
            print("Not connected to WiFi. Starting access point.")
            start_access_point()
        time.sleep(60)

if __name__ == '__main__':
    main()
EOT

# Create systemd service for Flask app
echo "Creating systemd service for Flask app..."
cat <<EOT > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/home/pizero/Dog_Feeder_V2
ExecStart=/usr/bin/python3 /home/pizero/Dog_Feeder_V2/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
systemctl daemon-reload

# Enable the Flask app service to start on boot
echo "Enabling Flask app service to start on boot..."
systemctl enable flaskapp.service

# Start the Flask app service immediately
echo "Starting Flask app service..."
systemctl start flaskapp.service

# Check the status of the Flask app service
systemctl status flaskapp.service --no-pager

# Create systemd service for WiFi manager
echo "Creating systemd service for WiFi manager..."
cat <<EOT > /etc/systemd/system/wifimanager.service
[Unit]
Description=WiFi Manager
After=network.target

[Service]
User=root
ExecStart=/usr/bin/python3 /home/pizero/Dog_Feeder_V2/wifi_manager.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
systemctl daemon-reload

# Enable the WiFi manager service to start on boot
echo "Enabling WiFi manager service to start on boot..."
systemctl enable wifimanager.service

# Start the WiFi manager service immediately
echo "Starting WiFi manager service..."
systemctl start wifimanager.service

# Check the status of the WiFi manager service
systemctl status wifimanager.service --no-pager

echo "Setup complete. You can now access your Flask app using http://feeder.local (after running the app)."
