#!/bin/bash
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
sudo systemctl mask hostapd
sudo \cp /etc/dhcpcd.orig.conf /etc/dhcpcd.conf
sudo systemctl enable wpa_supplicant
sudo systemctl start wpa_supplicant
sudo reboot