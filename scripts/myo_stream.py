import asyncio
import sys
import os
import json
import csv
from pylsl import StreamInfo, StreamOutlet
from time import sleep

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

CONFIG_FILE = os.path.join(BASE_DIR, '..', 'configs', 'emg_data_stream.json')

# Sampling frequency
Fs = 200
period_ms = 1 / Fs
duration = 2 * 60 * Fs  # 2 minutes of data

def load_config(path: str) -> dict:
    """
    Load the configuration from a JSON file.
    
    :param path: Path to the JSON file
    :type path: str
    :returns: Dictionary containing configuration data
    :rtype: dict
    """
    try:
        with open(path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the config file: {path}")
        sys.exit(1)

def load_data(path: str) -> list:
    """
    Load data from a CSV file.
    
    :param path: Path to the CSV file
    :type path: str
    :returns: List of data samples
    :rtype: list
    """
    results = []
    try:
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            for i, row in enumerate(reader):
                if i >= duration:
                    break  # Stop reading after loading the required duration
                results.append(row)
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"Error reading file {path}: {e}")
    return results

def stream_data(data: list, fs: int, stream: StreamOutlet):
    """
    Stream data in an infinite loop.
    
    :param data: Data to stream
    :type data: list
    :param fs: Sampling frequency
    :type fs: int
    :param stream: Lab Streaming Layer outlet
    :type stream: StreamOutlet
    """
    while True:
        for sample in data:
            stream.push_sample(sample)
            sleep(1 / fs)

# Load configuration
config = load_config(CONFIG_FILE)
stream_config = config['streams'][0]

# Extract stream parameters from config
stream_name = stream_config['name']
stream_type = stream_config['type']
sampling_frequency = stream_config['sampling_frequency']
data_type = stream_config['data_type']
unique_id = stream_config['unique_id']
channels = stream_config['channels']

# LSL configuration - use the parameters from the config
info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
outlet = StreamOutlet(info)

# Data file paths
data_files = [
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/index_finger_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/thumb_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/middle_finger_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/ring_finger_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/little_finger_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/rest_finger_motion_raw.csv"),
    os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed/victory_finger_motion_raw.csv")
]

# Load all data
all_data = []
for file in data_files:
    data = load_data(file)
    print(f"Loaded data from {file} with length {len(data)} -> {len(data) / Fs:.2f} seconds")
    all_data.extend(data)

# Stream data in an infinite loop
async def main():
    await asyncio.to_thread(stream_data, all_data, sampling_frequency, outlet)

if __name__ == "__main__":
    asyncio.run(main())
