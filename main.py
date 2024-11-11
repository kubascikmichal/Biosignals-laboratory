import os
import json
import subprocess
import time

# Define base paths as constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'configs')
LOG_DIR = os.path.join(BASE_DIR, 'logs')


# Ensure directories exist
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


ensure_directory(LOG_DIR)


def load_config_files(config_dir):
    """Load all JSON configuration files from a folder."""
    return [os.path.join(config_dir, f) for f in os.listdir(config_dir) if f.endswith('.json')]


def parse_config(file_path):
    """Parse a JSON configuration file, handling errors."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def start_stream(script_path, stream_config):
    """Start a script as a subprocess with logging."""
    log_file_path = os.path.join(LOG_DIR, f"{stream_config['name']}.log")
    with open(log_file_path, 'a') as log_file:
        return subprocess.Popen(
            ['python', script_path, stream_config['name'], stream_config['type']],
            stdout=log_file, stderr=subprocess.STDOUT
        )


def main():
    config_files = load_config_files(CONFIG_DIR)
    processes = []

    # Load configurations and start processes
    for config_file in config_files:
        config = parse_config(config_file)
        if not config:
            continue  # Skip files that couldn't be parsed

        for stream in config.get('streams', []):
            script_path = os.path.join(BASE_DIR, stream['script_path'])
            if not os.path.isfile(script_path):
                print(f"Error: Script file {script_path} does not exist. Skipping stream {stream['name']}.")
                continue

            process = start_stream(script_path, stream)
            if process:
                processes.append((stream, process, script_path))
                print(f"Started stream '{stream['name']}' with PID {process.pid}")

    # Monitor processes, restart if any terminate unexpectedly
    try:
        while processes:
            for i, (stream, process, script_path) in enumerate(processes):
                if process.poll() is not None:  # Process has ended
                    print(f"Process '{stream['name']}' (PID {process.pid}) ended. Restarting...")
                    process = start_stream(script_path, stream)
                    processes[i] = (stream, process, script_path)
                    print(f"Restarted stream '{stream['name']}' with new PID {process.pid}")
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("Shutting down all processes...")
        for stream, process, _ in processes:
            process.terminate()
            print(f"Terminated stream '{stream['name']}' (PID {process.pid})")


if __name__ == "__main__":
    main()
