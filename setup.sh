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
sed -i '/^host-name=/d' "$AVAHI_CONF"
sed -i '/\[server\]/a host-name=feeder' "$AVAHI_CONF"

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

# Check the status of the Flask app service
systemctl status flaskapp.service --no-pager

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
systemctl daemon-reload

echo "Setup complete. You can now access your Flask app using http://feeder.local (after running the app)."