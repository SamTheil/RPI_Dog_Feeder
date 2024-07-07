import os
import subprocess
import sys

class GitHubUpdater:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
    
    def check_for_updates(self):
        # Navigate to the repository directory
        os.chdir(self.repo_dir)
        # Fetch updates from the remote repository
        result = subprocess.run(["git", "fetch"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}

        # Check for changes between local and remote
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        
        if "Your branch is up to date" in result.stdout:
            return {"status": "up-to-date"}
        else:
            return {"status": "update-available"}

    def update_repo(self):
        # Navigate to the repository directory
        os.chdir(self.repo_dir)
        # Pull updates from the remote repository
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        return {"status": "updated", "message": result.stdout}