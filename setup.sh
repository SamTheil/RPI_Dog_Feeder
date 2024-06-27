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
apt-get install -y python3-flask python3-git python3-requests

# Create systemd service for Flask app
echo "Creating systemd service for Flask app..."
cat <<EOT > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/home/pizero/RPI_Dog_Feeder
ExecStart=/usr/bin/python3 /home/pizero/RPI_Dog_Feeder/app.py
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

sudo apt-get install hostapd dnsmasq

# Check the status of the Flask app service
systemctl status flaskapp.service --no-pager

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
systemctl daemon-reload

sudo tee /etc/dhcpcd.orig.conf << 'EOF'
# Original dhcpcd.conf content
# Example configuration:

hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option interface_mtu
require dhcp_server_identifier
slaac private
# Additional original configurations...
EOF

sudo tee /etc/dhcpcd.accesspoint.conf << 'EOF'
# Modified dhcpcd.conf content for access point
hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option interface_mtu
require dhcp_server_identifier
slaac private

# Static IP configuration for access point
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
# Additional access point configurations...
EOF

sudo tee /etc/hostapd/hostapd.conf << 'EOF'
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
rsn_pairwise=CCMP
EOF

sudo tee /etc/dnsmasq.conf << 'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

sudo sed -i 's|#DAEMON_CONF="|DAEMON_CONF="/etc/hostapd/hostapd.conf|' /etc/default/hostapd


echo "Setup complete. You can now access your Flask app using http://feeder.local (after running the app)."