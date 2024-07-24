import csv
import time
from pylsl import StreamInlet, resolve_stream

# Configuration
OUTPUT_FILE = 'stream1_data_log.csv'  # The name of the file to store the data
STREAM_NAME = 'Stream1'  # Replace with the name of your LSL stream

def find_stream(name):
    """Finds an LSL stream with the given name."""
    print(f"Searching for stream: {name}")
    # Resolving all available streams
    streams = resolve_stream('name', name)
    if not streams:
        raise RuntimeError(f"No streams found with name: {name}")
    return streams[0]

def main():
    # Find the data source
    stream = find_stream(STREAM_NAME)
    inlet = StreamInlet(stream)
    
    # Open the CSV file for writing
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        print(f"Starting data logging for {STREAM_NAME}...")
        
        # Write the header of the CSV
        writer.writerow(['Timestamp'] + [f'Channel_{i}' for i in range(stream.channel_count())])
        
        try:
            while True:
                # Get data from the stream
                timestamp, data = inlet.pull_sample()
                
                # Write data to the CSV file
                writer.writerow([timestamp] + data)
                
                # Print to console (optional)
                print(f"Timestamp: {timestamp}, Data: {data}")
                
                # Wait a bit before the next read
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Data logging stopped.")

if __name__ == "__main__":
    main()
