#!/bin/bash
sudo \cp /etc/dhcpcd.accesspoint.conf /etc/dhcpcd.conf
sudo systemctl stop wpa_supplicant
sudo systemctl disable wpa_supplicant
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
sudo reboot