import os
import json
import subprocess
import time

# base pathway of the proyect
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# config folder
CONFIG_DIR = os.path.join(BASE_DIR, 'configs')es

def load_config_files(config_dir):
    """Load all the JSON config files from a folder"""
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    return [os.path.join(config_dir, f) for f in config_files]

def parse_config(file_path):
    """Parse a JSON config file"""
    with open(file_path, 'r') as file:
        return json.load(file)

def start_stream(script_path):
    """Starts an script and returns the process"""
    return subprocess.Popen(['python', script_path])

def main():
    config_files = load_config_files(CONFIG_DIR)
    processes = []
    
    for config_file in config_files:
        config = parse_config(config_file)
        for stream in config['streams']:
            script_path = os.path.join(BASE_DIR, stream['script_path'])
            process = start_stream(script_path)
            processes.append((stream['name'], process))
            print(f"Started {stream['name']} with PID {process.pid}")
    
    # Monitor the processes
    try:
        while True:
            for name, process in processes:
                if process.poll() is not None:  # process finished
                    print(f"Process {name} (PID {process.pid}) ended.")
                    # reset the process if necessary
                    script_path = [stream['script_path'] for stream in parse_config(config_file)['streams'] if stream['name'] == name][0]
                    process = start_stream(script_path)
                    processes.append((name, process))
                    print(f"Restarted {name} with PID {process.pid}")
            time.sleep(5)  # wait before retry
    except KeyboardInterrupt:
        print("Shutting down...")
        for name, process in processes:
            process.terminate()
            print(f"Terminated {name} (PID {process.pid})")

if __name__ == "__main__":
    main()
