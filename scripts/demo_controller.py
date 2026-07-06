import serial
import time
import sys

ESP32_PORT = '/dev/ttyUSB0'
RADIO_PORT = '/dev/ttyS2'
ESP32_BAUD = 115200
RADIO_BAUD = 9600

def get_temp_from_esp32(esp32_serial):
    try:
        # Flush input buffer to clear old ACKs
        esp32_serial.reset_input_buffer()
        # Request temperature
        esp32_serial.write(b"TEMP\n")
        
        # Wait up to 2 seconds for the ESP32 to respond (reading 1-wire takes ~750ms)
        timeout = time.time() + 2
        while time.time() < timeout:
            if esp32_serial.in_waiting > 0:
                resp = esp32_serial.readline().decode('utf-8').strip()
                if "ACK" not in resp: # Ignore stray motor ACKs
                    try:
                        return float(resp)
                    except ValueError:
                        pass
            time.sleep(0.1)
    except Exception as e:
        print(f"Error reading temp from ESP32: {e}")
    return -999.0

def main():
    print("Starting Orange Pi Demo Controller...")
    
    try:
        esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
        print(f"Connected to ESP32 on {ESP32_PORT}", flush=True)
    except Exception as e:
        print(f"Failed to connect to ESP32: {e}")
        return

    try:
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
        print(f"Connected to Radio on {RADIO_PORT}", flush=True)
    except Exception as e:
        print(f"Failed to connect to Radio: {e}")
        return

    print("\nWaiting for 'START' command from Laptop via Radio... (Press Ctrl+C on this keyboard to bypass and force start)", flush=True)
    try:
        while True:
            if radio.in_waiting > 0:
                msg = radio.readline().decode('utf-8', errors='ignore').strip()
                if msg == "START":
                    print("Start command received! Beginning 40-second demonstration.", flush=True)
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n[KEYBOARD OVERRIDE] Radio bypassed. Forcing the demonstration to start right now!", flush=True)

    print("Moving Forward...")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print("Stopping to sample Cold Water...")
    esp32.write(b"STOP\n")
    time.sleep(2) 
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"Cold Temp read: {temp_c} C")
    radio.write(f"COLD_TEMP: {temp_c:.2f} C\n".encode('utf-8'))
    time.sleep(3)

    print("Moving Forward to Hot Bowl...")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print("Stopping to sample Hot Water...")
    esp32.write(b"STOP\n")
    time.sleep(2)
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"Hot Temp read: {temp_c} C")
    radio.write(f"HOT_TEMP: {temp_c:.2f} C\n".encode('utf-8'))
    time.sleep(3)

    print("Demonstration Complete!")

if __name__ == '__main__':
    main()
