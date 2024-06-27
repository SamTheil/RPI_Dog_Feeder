import subprocess
import os

# Get the current directory where the Python script is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the path to the setup.sh file
setup_script_path = os.path.join(current_directory, 'setup.sh')

# Run the setup.sh file
try:
    result = subprocess.run(['bash', setup_script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Script output:", result.stdout.decode())
except subprocess.CalledProcessError as e:
    print("An error occurred while running the script.")
    print("Error output:", e.stderr.decode())