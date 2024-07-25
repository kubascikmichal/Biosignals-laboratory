import asyncio
from bleak import BleakClient, BleakScanner
from pylsl import StreamInfo, StreamOutlet

# BLE device MAC address (adjust as necessary)
DEVICE_MAC_ADDRESS = "fb:36:a9:c9:22:69"  # Replace with your device's MAC address

# UUIDs for the service and characteristic (adjust if necessary)
SERVICE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a56-0000-1000-8000-00805f9b34fb"

# LSL configuration
info = StreamInfo('SensorStream', 'EEG', 1, 100, 'float32', 'myuidw43536')
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

