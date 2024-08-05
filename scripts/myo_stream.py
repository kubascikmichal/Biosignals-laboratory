import asyncio
import sys
import os
from pylsl import StreamInfo, StreamOutlet
import csv
from time import sleep

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data folder
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Sampling frequency
Fs = 200
period_ms = 1 / Fs
duration = 2 * 60 * Fs  # 2 minutes of data

# Get parameters from command line arguments
if len(sys.argv) < 6:
    print("Usage: python %s <stream_name> <stream_type> <sampling_frequency> <data_type> <unique_id> <channels>" % (sys.argv[0]))
    sys.exit(1)

stream_name = sys.argv[1]
stream_type = sys.argv[2]
sampling_frequency = int(sys.argv[3])
data_type = sys.argv[4]
unique_id = sys.argv[5]
channels = sys.argv[6].split(',')

# LSL configuration - use the parameters from command line arguments
info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
outlet = StreamOutlet(info)

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
    await asyncio.to_thread(stream_data, all_data, Fs, outlet)

if __name__ == "__main__":
    asyncio.run(main())

