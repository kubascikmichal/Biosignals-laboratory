import asyncio
import os
import json
import sys
from bleak import BleakClient, BleakScanner
from pylsl import StreamInfo, StreamOutlet

# Define paths and constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, '..', 'configs', 'ecg_data_stream.json')
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')
DEVICE_MAC_ADDRESS = "fb:36:a9:c9:22:69"
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
CHARACTERISTIC_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


# Load configuration from JSON file
def load_config(path: str) -> dict:
    """Load JSON configuration file."""
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


# Log sensor data to file
def log_data(value: int):
    """Append sensor data to log file."""
    log_message = f"Sensor value: {value}\n"
    with open(os.path.join(LOG_DIR, 'sensor_data.log'), 'a') as log_file:
        log_file.write(log_message)


# BLE notification handler function
def notification_handler(sender, data, outlet):
    """Process BLE notification and send data to LSL stream."""
    sensor_value = int.from_bytes(data, byteorder='little')
    log_data(sensor_value)
    outlet.push_sample([sensor_value])


async def run():
    config = load_config(CONFIG_FILE)
    stream_config = config['streams'][0]

    # Initialize LSL stream with configuration
    info = StreamInfo(
        name=stream_config['name'],
        type=stream_config['type'],
        channel_count=len(stream_config['channels']),
        nominal_srate=stream_config['sampling_frequency'],
        channel_format=stream_config['data_type'],
        source_id=stream_config['unique_id']
    )
    outlet = StreamOutlet(info)

    # Scan for and connect to the BLE device
    device = await BleakScanner.find_device_by_address(DEVICE_MAC_ADDRESS)
    if not device:
        print("Device not found!")
        return

    async with BleakClient(device) as client:
        print("Connected to the BLE device")
        await client.start_notify(CHARACTERISTIC_UUID, lambda sender, data: notification_handler(sender, data, outlet))

        # Keep the script running to receive data
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Stopping the stream...")
        finally:
            await client.stop_notify(CHARACTERISTIC_UUID)


if __name__ == "__main__":
    asyncio.run(run())
