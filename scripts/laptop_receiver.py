import serial
import time
import sys

# CHANGE THIS TO YOUR LAPTOP'S RADIO COM PORT (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Mac/Linux)
LAPTOP_RADIO_PORT = 'COM4' 
BAUD_RATE = 115200

def main():
    print("--- ASV Ground Station (Laptop) ---")
    
    try:
        radio = serial.Serial(LAPTOP_RADIO_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Radio on {LAPTOP_RADIO_PORT}")
    except Exception as e:
        print(f"ERROR: Could not connect to {LAPTOP_RADIO_PORT}. Please check your COM port!")
        print(f"Exception: {e}")
        sys.exit(1)

    print("\nPress ENTER to transmit the START command to the Orange Pi...")
    input()
    
    print("Transmitting START...")
    radio.write(b"START\n")
    
    print("\n--- Listening for Telemetry from ASV ---")
    print("(Waiting for Temperature Readings...)\n")
    
    while True:
        try:
            if radio.in_waiting > 0:
                msg = radio.readline().decode('utf-8', errors='ignore').strip()
                if msg:
                    # Print loudly for the presentation!
                    print("="*40)
                    print(f">>> ASV TELEMETRY RECEIVED: {msg}")
                    print("="*40)
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting Ground Station.")
            break

if __name__ == '__main__':
    main()
