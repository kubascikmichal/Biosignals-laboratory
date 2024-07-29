import os
import json
import subprocess
import time

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration folder
CONFIG_DIR = os.path.join(BASE_DIR, 'configs')

# Log folder
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Create log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def load_config_files(config_dir):
    """Loads all JSON configuration files from a folder."""
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    return [os.path.join(config_dir, f) for f in config_files]

def parse_config(file_path):
    """Parses a JSON configuration file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def start_stream(script_path, stream_name, stream_type):
    """Starts a script and returns the process."""
    log_file = os.path.join(LOG_DIR, f'{stream_name}.log')
    return subprocess.Popen(['python', script_path, stream_name, stream_type], stdout=open(log_file, 'a'), stderr=subprocess.STDOUT)

def main():
    config_files = load_config_files(CONFIG_DIR)
    processes = []
    
    # Load configurations and start processes
    for config_file in config_files:
        config = parse_config(config_file)
        for stream in config['streams']:
            # Construct the absolute path to the script
            script_path = os.path.join(BASE_DIR, stream['script_path'])
            if not os.path.isfile(script_path):
                print(f"Error: The file {script_path} does not exist.")
                continue
            process = start_stream(script_path, stream['name'], stream['type'])
            processes.append((stream['name'], process, script_path))
            print(f"Started {stream['name']} with PID {process.pid}")
    
    # Monitor the processes
    try:
        while True:
            for i, (name, process, script_path) in enumerate(processes):
                if process.poll() is not None:  # Process has ended
                    print(f"Process {name} (PID {process.pid}) ended.")
                    # Restart the process if necessary
                    process = start_stream(script_path, name, 'type')  # Provide appropriate type here if needed
                    processes[i] = (name, process, script_path)
                    print(f"Restarted {name} with PID {process.pid}")
            time.sleep(5)  # Wait before checking again
    except KeyboardInterrupt:
        print("Shutting down...")
        for name, process, _ in processes:
            process.terminate()
            print(f"Terminated {name} (PID {process.pid})")

if __name__ == "__main__":
    main()
