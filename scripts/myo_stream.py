import asyncio
import sys
from pylsl import StreamInfo, StreamOutlet
import csv

# Get parameters from command line arguments
#if len(sys.argv) < 6:
#    print("Usage: python %s <stream_name> <stream_type> <sampling_frequency> <data_type> <unique_id> <channels>" % (sys.argv[0]))
#    sys.exit(1)

#stream_name = sys.argv[1]
#stream_type = sys.argv[2]
#sampling_frequency = sys.argv[3]
#data_type = sys.argv[4]
#unique_id = sys.argv[5]
#channels = sys.argv[6].split(',')

# LSL configuration - use the parameters from command line arguments
#info = StreamInfo(stream_name, stream_type, len(channels), sampling_frequency, data_type, unique_id)
#outlet = StreamOutlet(info)

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
            results.append(row)
    return len(results)

thumb_results=[]
len = load_data(thumb_results, "../data/myo_stream/raw_emg_data_unprocessed/thumb_motion_raw.csv")
print("Loaded thumb movement data with len %d" % len)
index_results=[]
len = load_data(index_results, "..\\data\\myo_stream\\raw_emg_data_unprocessed\\index_finger_motion_raw.csv")
print("Loaded index movement data with len %d" % len)
middle_results=[]
len = load_data(middle_results, "..\\data\\myo_stream\\raw_emg_data_unprocessed\\middle_finger_motion_raw.csv")
print("Loaded middle movement data with len %d" % len)
rest_results=[]
len = load_data(rest_results, "..\\data\\myo_stream\\raw_emg_data_unprocessed\\rest_finger_motion_raw.csv")
print("Loaded rest movement data with len %d" % len)
little_results=[]
len = load_data(little_results, "..\\data\\myo_stream\\raw_emg_data_unprocessed\\middle_finger_motion_raw.csv")
print("Loaded little movement data with len %d" % len)
