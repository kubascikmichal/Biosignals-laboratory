import time

def stream1():
    print("Starting Stream1 (EEG)...")
    while True:
        # Simulate the transmision of EEG data
        print("Streaming EEG data...")
        time.sleep(1)

if __name__ == "__main__":
    stream1()
