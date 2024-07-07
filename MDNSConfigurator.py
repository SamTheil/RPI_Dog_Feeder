import subprocess

class MdnsConfigurator:
    def __init__(self):
        self.avahi_conf = "/etc/avahi/avahi-daemon.conf"
        self.hostname_file = "/etc/hostname"
        self.hosts_file = "/etc/hosts"

    def set_hostname(self, new_hostname):
        self._update_hostname_file(new_hostname)
        self._update_hosts_file(new_hostname)
        self._apply_hostname_changes(new_hostname)
        self._configure_avahi_daemon(new_hostname)
        self._restart_avahi_daemon()
    
    def _update_hostname_file(self, new_hostname):
        subprocess.run(["sudo", "sh", "-c", f"echo {new_hostname} > {self.hostname_file}"], check=True)
        print(f"Hostname set to '{new_hostname}' in {self.hostname_file}")

    def _update_hosts_file(self, new_hostname):
        subprocess.run(["sudo", "sh", "-c", f"echo '127.0.0.1       localhost' > {self.hosts_file}"], check=True)
        subprocess.run(["sudo", "sh", "-c", f"echo '127.0.1.1       {new_hostname}' >> {self.hosts_file}"], check=True)
        print(f"Hosts file updated in {self.hosts_file}")

    def _apply_hostname_changes(self, new_hostname):
        subprocess.run(["sudo", "hostnamectl", "set-hostname", new_hostname], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "systemd-hostnamed"], check=True)
        print("Hostname changes applied and systemd-hostnamed restarted")

    def _configure_avahi_daemon(self, new_hostname):
        subprocess.run(["sudo", "sed", "-i", "/^host-name=/d", self.avahi_conf], check=True)
        subprocess.run(["sudo", "sed", "-i", f"/\\[server\\]/a host-name={new_hostname}", self.avahi_conf], check=True)
        subprocess.run(["sudo", "sed", "-i", "/\\[server\\]/a ratelimit-burst=1000", self.avahi_conf], check=True)
        subprocess.run(["sudo", "sed", "-i", "/\\[server\\]/a ratelimit-interval-usec=1000000", self.avahi_conf], check=True)
        if not subprocess.run(["sudo", "grep", "-q", "^log-level=", self.avahi_conf], check=False).returncode == 0:
            subprocess.run(["sudo", "sed", "-i", "/\\[server\\]/a log-level=debug", self.avahi_conf], check=True)
        print(f"Avahi daemon configured in {self.avahi_conf}")

    def _restart_avahi_daemon(self):
        subprocess.run(["sudo", "systemctl", "restart", "avahi-daemon"], check=True)
        print("Avahi daemon restarted")

# Usage
if __name__ == "__main__":
    mdns_configurator = MdnsConfigurator()
    new_hostname = "feeder2"
    mdns_configurator.set_hostname(new_hostname)
    print(f"mDNS name changed to {new_hostname}.local")