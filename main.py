import os
import json
import subprocess

CONFIG_DIR = 'path/to/config/folder'

def load_config_files(config_dir):
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    return [os.path.join(config_dir, f) for f in config_files]

def parse_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def start_stream(script_path):
    return subprocess.Popen(['python', script_path])

def main():
    config_files = load_config_files(CONFIG_DIR)
    processes = []
    
    for config_file in config_files:
        config = parse_config(config_file)
        for stream in config['streams']:
            script_path = stream['script_path']
            process = start_stream(script_path)
            processes.append((stream['name'], process))
    
    # Optionally, monitor the processes or add more logic here
    for name, process in processes:
        process.wait()  # This will wait for the process to finish

if __name__ == "__main__":
    main()
