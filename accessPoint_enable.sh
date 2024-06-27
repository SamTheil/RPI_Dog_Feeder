sudo \cp /etc/dhcpcd.accesspoint.conf /etc/dhcpcd.conf;
sudo systemctl enable hostapd;
sudo systemctl enable dnsmasq;
sudo reboot;