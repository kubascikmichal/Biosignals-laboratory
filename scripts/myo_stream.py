import asyncio
import sys
from pylsl import StreamInfo, StreamOutlet
import csv
from time import sleep

Fs = 200
period_ms = 1/Fs
duration = 2 * 60 * Fs  # 2 minutes of data

# Get parameters from command line arguments
if len(sys.argv) < 6:
    print("Usage: python %s <stream_name> <stream_type> <sampling_frequency> <data_type> <unique_id> <channels>" % (sys.argv[0]))
    sys.exit(1)

stream_name = sys.argv[1]
stream_type = sys.argv[2]
sampling_frequency = sys.argv[3]
data_type = sys.argv[4]
unique_id = sys.argv[5]
channels = sys.argv[6].split(',')

# LSL configuration - use the parameters from command line arguments
info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
outlet = StreamOutlet(info)

def load_data(results: list, path: str) -> int:
    """
    :param results: list of float
    :type results: list
    :param path: path to csv file
    :type path: str
    :returns: len of data
    :rtype: int
    """
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            if i >= duration:
                break  # Stop reading after loading the required duration
            results.append(row)
    return len(results)

def stream_data(data: list, fs:int, stream: StreamOutlet):
    """
    :param data: data to stream
    :type data: list
    :param fs: sampling frequency
    :type fs: int
    :param stream: Lab Streaming Layer outlet
    :type stream: StreamOutlet
    """
    while True:
    for i in range(len(data)):
        stream.push_sample(data[i])
        sleep(1/fs)

# Load the first two minutes of data from each CSV file
index_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\index_finger_motion_raw.csv", duration)
print("Loaded index movement data with len %d -> %0.2f seconds" % (len(index_results), len(index_results) / Fs))

thumb_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\thumb_motion_raw.csv", duration)
print("Loaded thumb movement data with len %d -> %0.2f seconds" % (len(thumb_results), len(thumb_results) / Fs))

middle_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\middle_finger_motion_raw.csv", duration)
print("Loaded middle movement data with len %d -> %0.2f seconds" % (len(middle_results), len(middle_results) / Fs))

ring_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\ring_finger_motion_raw.csv", duration)
print("Loaded ring movement data with len %d -> %0.2f seconds" % (len(ring_results), len(ring_results) / Fs))

little_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\little_finger_motion_raw.csv", duration)
print("Loaded little movement data with len %d -> %0.2f seconds" % (len(little_results), len(little_results) / Fs))

rest_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\rest_finger_motion_raw.csv", duration)
print("Loaded rest movement data with len %d -> %0.2f seconds" % (len(rest_results), len(rest_results) / Fs))

victory_results = load_data("data\\myo_stream\\raw_emg_data_unprocessed\\victory_finger_motion_raw.csv", duration)
print("Loaded victory movement data with len %d -> %0.2f seconds" % (len(victory_results), len(victory_results) / Fs))

# Stream data in an infinite loop
async def main():
    await asyncio.gather(
        asyncio.to_thread(stream_data, index_results, Fs, outlet),
        asyncio.to_thread(stream_data, thumb_results, Fs, outlet),
        asyncio.to_thread(stream_data, middle_results, Fs, outlet),
        asyncio.to_thread(stream_data, ring_results, Fs, outlet),
        asyncio.to_thread(stream_data, little_results, Fs, outlet),
        asyncio.to_thread(stream_data, rest_results, Fs, outlet),
        asyncio.to_thread(stream_data, victory_results, Fs, outlet)
    )

if __name__ == "__main__":
    asyncio.run(main())
