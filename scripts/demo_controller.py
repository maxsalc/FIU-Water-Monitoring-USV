import serial
import time
import sys

RADIO_PORT = '/dev/ttyS7'     # UART7 on Orange Pi 4 Pro
RADIO_BAUD = 9600

ESP32_PORT = '/dev/ttyUSB0'   # USB connection to ESP32
ESP32_BAUD = 115200

def get_temp_from_esp32(esp32_serial):
    try:
        esp32_serial.reset_input_buffer()
        esp32_serial.write(b"TEMP\n")
        
        timeout = time.time() + 3
        while time.time() < timeout:
            if esp32_serial.in_waiting > 0:
                resp = esp32_serial.readline().decode('utf-8', errors='ignore').strip()
                if resp and "ACK" not in resp and "ESP32" not in resp:
                    try:
                        return float(resp)
                    except ValueError:
                        pass
        return -999.0
    except Exception as e:
        print(f"Error reading temp from ESP32: {e}")
        return -999.0

def main():
    print("Starting Orange Pi Demo Controller...")
    
    try:
        esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
        esp32.setDTR(False)
        esp32.setRTS(False)
        print(f"Connected to ESP32 on {ESP32_PORT}... Waiting for bootup.")
        time.sleep(2.5) 
        esp32.reset_input_buffer()
        print("ESP32 Ready!")
    except Exception as e:
        print(f"Failed to connect to ESP32: {e}")
        return

    try:
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
        print(f"Connected to Radio on {RADIO_PORT}")
    except Exception as e:
        print(f"Failed to connect to Radio: {e}")
        return

    print("\nWaiting for 'START' command from Laptop via Radio...")
    
    # Block until START is received
    while True:
        if radio.in_waiting > 0:
            msg = radio.readline().decode('utf-8', errors='ignore').strip()
            if "START" in msg:
                print("Received START command! Beginning Demonstration.")
                break
        time.sleep(0.1)

    # --- THE DEMONSTRATION LOGIC ---
    
    print("\n>>> MOVING FORWARD (10 seconds)")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print(">>> STOPPING to sample Cold Water...")
    esp32.write(b"STOP\n")
    time.sleep(2) 
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"    [SENSOR DATA] Cold Water Temp: {temp_c} C")
    radio.write(f"TEMP:{temp_c}\n".encode('utf-8'))
    time.sleep(3)

    print("\n>>> MOVING FORWARD to Hot Bowl (10 seconds)")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print(">>> STOPPING to sample Hot Water...")
    esp32.write(b"STOP\n")
    time.sleep(2)
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"    [SENSOR DATA] Hot Water Temp: {temp_c} C")
    radio.write(f"TEMP:{temp_c}\n".encode('utf-8'))

    print("\nDemonstration Complete! Waiting for next command...")

if __name__ == '__main__':
    main()
