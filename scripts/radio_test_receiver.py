import serial
import time

PORT = '/dev/ttyS7' 
BAUD = 9600

def main():
    print(f"Starting Radio Receiver on {PORT} at {BAUD} baud...")
    try:
        radio = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return
        
    print("Listening for messages...")
    while True:
        if radio.in_waiting > 0:
            msg = radio.readline().decode('utf-8', errors='ignore').strip()
            if msg:
                print(f"Received: {msg}")
        time.sleep(0.1)

if __name__ == '__main__':
    main()
