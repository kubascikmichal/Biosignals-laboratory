import asyncio
import sys
from bleak import BleakClient, BleakScanner
from pylsl import StreamInfo, StreamOutlet

# BLE device MAC address and UUIDs (adjust as necessary)
DEVICE_MAC_ADDRESS = "fb:36:a9:c9:22:69"
SERVICE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a56-0000-1000-8000-00805f9b34fb"


def parse_args():
    """Parse command-line arguments for LSL configuration."""
    if len(sys.argv) < 7:
        print(
            "Usage: python script.py <stream_name> <stream_type> <sampling_frequency> <data_type> <unique_id> "
            "<channels>")
        sys.exit(1)

    # Extract command-line arguments
    stream_name = sys.argv[1]
    stream_type = sys.argv[2]
    sampling_frequency = int(sys.argv[3])
    data_type = sys.argv[4]
    unique_id = sys.argv[5]
    channels = sys.argv[6].split(',')

    return stream_name, stream_type, sampling_frequency, data_type, unique_id, channels


def create_stream_outlet(stream_name, stream_type, sampling_frequency, data_type, unique_id, channels):
    """Set up the LSL stream outlet with the given parameters."""
    info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
    return StreamOutlet(info)


def notification_handler(sender, data):
    """Handle BLE notifications and push data to LSL stream."""
    sensor_value = int.from_bytes(data, byteorder='little')
    print(f"Sensor value: {sensor_value}")
    outlet.push_sample([sensor_value])


async def run(outlet):
    """Scan for the BLE device, connect, and start notifications."""
    device = await BleakScanner.find_device_by_address(DEVICE_MAC_ADDRESS)
    if not device:
        print("Device not found!")
        return

    async with BleakClient(device) as client:
        print("Connected to BLE device")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

        # Keep the script running to receive data
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("BLE notification loop stopped")


if __name__ == "__main__":
    # Parse arguments and create LSL stream outlet
    stream_name, stream_type, sampling_frequency, data_type, unique_id, channels = parse_args()
    outlet = create_stream_outlet(stream_name, stream_type, sampling_frequency, data_type, unique_id, channels)

    # Run the BLE notification handling asynchronously
    asyncio.run(run(outlet))
