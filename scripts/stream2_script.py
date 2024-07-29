import time
from pylsl import StreamInfo, StreamOutlet

def stream2():
    print("Starting Stream1 (Random)...")
    
    # LSL configuration - needs to be loaded from config file
    info = StreamInfo('DefultStream', 'Test', 1, 1, 'float32', 'myuidw43536')
    outlet = StreamOutlet(info)
    while True:
        outlet.push_sample([1])
        time.sleep(1)

if __name__ == "__main__":
    stream2()
