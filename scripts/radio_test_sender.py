import serial
import time

PORT = 'COM4' 
BAUD = 9600

def main():
    print(f"Starting Radio Sender on {PORT} at {BAUD} baud...")
    try:
        radio = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return
        
    counter = 1
    while True:
        msg = f"TEST MESSAGE {counter}\n"
        print(f"Sending: {msg.strip()}")
        radio.write(msg.encode('utf-8'))
        counter += 1
        time.sleep(2)

if __name__ == '__main__':
    main()
