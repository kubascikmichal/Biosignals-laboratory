import asyncio
import sys
import os
import json
from bleak import BleakClient, BleakScanner
from pylsl import StreamInfo, StreamOutlet
from time import sleep

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration file path
CONFIG_FILE = os.path.join(BASE_DIR, '..', 'configs', 'ecg_data_stream.json')

# Log directory path
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')

# Create log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Device BLE MAC address (adjust as needed)
DEVICE_MAC_ADDRESS = "fb:36:a9:c9:22:69"  # Replace with your device's MAC address

# UUIDs for the service and characteristic (adjust if needed)
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
CHARACTERISTIC_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Sampling frequency
Fs = 200
period_ms = 1 / Fs

# Load configuration from JSON
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

# Handle BLE notifications and push data to LSL stream
def notification_handler(sender, data, stream):
    """
    BLE notification handler that pushes data to the LSL outlet.
    
    :param sender: BLE sender identifier
    :param data: Data received from the BLE device
    :param stream: LSL outlet to transmit data
    """
    sensor_value = int.from_bytes(data, byteorder='little')
    log_message = f"Sensor value: {sensor_value}\n"

    # Write the sensor value to the log file
    with open(os.path.join(LOG_DIR, 'sensor_data.log'), 'a') as log_file:
        log_file.write(log_message)

    # Push the data to the LSL stream
    stream.push_sample([sensor_value])  # Send the data to the LSL stream

async def run():
    device = await BleakScanner.find_device_by_address(DEVICE_MAC_ADDRESS)
    if not device:
        print("Device not found!")
        return

    async with BleakClient(device) as client:
        print("Connected to the BLE device")
        
        # LSL configuration
        config = load_config(CONFIG_FILE)
        stream_config = config['streams'][0]
        
        stream_name = stream_config['name']
        stream_type = stream_config['type']
        sampling_frequency = stream_config['sampling_frequency']
        data_type = stream_config['data_type']
        unique_id = stream_config['unique_id']
        channels = stream_config['channels']

        # LSL StreamInfo and StreamOutlet
        info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
        outlet = StreamOutlet(info)

        # Start BLE notifications and stream to LSL
        await client.start_notify(CHARACTERISTIC_UUID, lambda sender, data: notification_handler(sender, data, outlet))

        # Keep the program running to receive data
        try:
            while True:
                await asyncio.sleep(1)  # Keep the loop active
        except KeyboardInterrupt:
            print("Stopping the stream...")
        finally:
            await client.stop_notify(CHARACTERISTIC_UUID)

# Run the script
if __name__ == "__main__":
    asyncio.run(run())
