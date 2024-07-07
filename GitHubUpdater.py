import os
import subprocess

class GitHubUpdater:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.configure_safe_directory()

    def configure_safe_directory(self):
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", self.repo_dir])

    def check_for_updates(self):
        os.chdir(self.repo_dir)
        result = subprocess.run(["git", "fetch"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        if "Your branch is up to date" in result.stdout:
            return {"status": "up-to-date"}
        else:
            return {"status": "update-available"}

    def update_repo(self):
        os.chdir(self.repo_dir)
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        return {"status": "updated", "message": result.stdout}
    
    def reboot_device(self):
        subprocess.run(["sudo", "reboot"])
