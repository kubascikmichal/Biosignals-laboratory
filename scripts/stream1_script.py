import asyncio
import sys
from bleak import BleakClient, BleakScanner
from pylsl import StreamInfo, StreamOutlet

# BLE device MAC address (adjust as necessary)
DEVICE_MAC_ADDRESS = "fb:36:a9:c9:22:69"  # Replace with your device's MAC address

# UUIDs for the service and characteristic (adjust if necessary)
SERVICE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a56-0000-1000-8000-00805f9b34fb"

# Get parameters from command line arguments
if len(sys.argv) < 6:
    print("Usage: python script.py <stream_name> <stream_type> <sampling_frequency> <data_type> <unique_id> <channels>")
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

def notification_handler(sender, data):
    """BLE notification handler function."""
    sensor_value = int.from_bytes(data, byteorder='little')
    print(f"Sensor value: {sensor_value}")
    outlet.push_sample([sensor_value])

async def run():
    device = await BleakScanner.find_device_by_address(DEVICE_MAC_ADDRESS)
    if not device:
        print("Device not found!")
        return

    async with BleakClient(device) as client:
        print("Connected to BLE device")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

        # Keep the program running to receive data
        while True:
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
