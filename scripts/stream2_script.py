import asyncio
from pylsl import StreamInfo, StreamOutlet


def initialize_stream(name='DefaultStream', stream_type='Test', channels=1, sampling_rate=1, data_type='float32',
                      uid='myuidw43536'):
    """Initialize and return an LSL StreamOutlet."""
    info = StreamInfo(name, stream_type, channels, sampling_rate, data_type, uid)
    return StreamOutlet(info)


async def stream_data(outlet, sample=[1], interval=1):
    """Push sample data to the LSL outlet at regular intervals."""
    print("Starting Stream...")
    while True:
        outlet.push_sample(sample)
        await asyncio.sleep(interval)


async def main():
    outlet = initialize_stream()
    await stream_data(outlet)


if __name__ == "__main__":
    asyncio.run(main())
