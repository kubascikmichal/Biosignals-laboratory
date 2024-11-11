import asyncio
import sys
import os
import json
import csv
from pylsl import StreamInfo, StreamOutlet

# Define constants and paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
CONFIG_FILE = os.path.join(BASE_DIR, '..', 'configs', 'emg_data_stream.json')
DURATION = 2 * 60 * 200  # 2 minutes of data at 200 Hz


def load_config(path: str) -> dict:
    """Load the JSON configuration file."""
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def load_data(path: str) -> list:
    """Load data samples from a CSV file, up to the specified duration."""
    samples = []
    try:
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            samples = [row for i, row in enumerate(reader) if i < DURATION]
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"Error reading file {path}: {e}")
    return samples


async def stream_data(all_data: list, fs: int, stream: StreamOutlet):
    """Stream data in a cyclic manner for each loaded dataset."""
    interval = 1 / fs
    while True:
        for data in all_data:
            for sample in data:
                stream.push_sample(sample)
                await asyncio.sleep(interval)


def initialize_lsl_stream(config) -> StreamOutlet:
    """Set up LSL StreamOutlet based on the configuration."""
    stream_cfg = config['streams'][0]
    info = StreamInfo(
        name=stream_cfg['name'],
        type=stream_cfg['type'],
        channel_count=len(stream_cfg['channels']),
        nominal_srate=stream_cfg['sampling_frequency'],
        channel_format=stream_cfg['data_type'],
        source_id=stream_cfg['unique_id']
    )
    return StreamOutlet(info)


async def main():
    # Load configuration and initialize stream
    config = load_config(CONFIG_FILE)
    outlet = initialize_lsl_stream(config)

    # Define paths and load data from all files
    data_files = [
        "index_finger_motion_raw.csv",
        "thumb_motion_raw.csv",
        "middle_finger_motion_raw.csv",
        "ring_finger_motion_raw.csv",
        "little_finger_motion_raw.csv",
        "rest_finger_motion_raw.csv",
        "victory_finger_motion_raw.csv"
    ]
    all_data = [load_data(os.path.join(DATA_DIR, "myo_stream/raw_emg_data_unprocessed", file)) for file in data_files]

    # Stream data asynchronously
    await stream_data(all_data, config['streams'][0]['sampling_frequency'], outlet)


if __name__ == "__main__":
    asyncio.run(main())
