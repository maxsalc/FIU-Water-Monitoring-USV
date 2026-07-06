import serial
import time
import sys

ESP32_PORT = '/dev/ttyUSB0'
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
            time.sleep(0.1)
    except Exception as e:
        print(f"Error reading temp from ESP32: {e}")
    return -999.0

def main():
    print("====================================")
    print("   ASV LOCAL DEMONSTRATION MODE")
    print("====================================")
    
    try:
        esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
        print(f"Connected to ESP32 on {ESP32_PORT}... Waiting for bootup.")
        # CRITICAL FIX: When Python opens a Serial port, the ESP32 reboots. 
        # We MUST wait 2 seconds for it to finish booting before sending commands!
        time.sleep(2.5) 
        esp32.reset_input_buffer()
        print("ESP32 Ready!")
    except Exception as e:
        print(f"Failed to connect to ESP32: {e}")
        return

    print("\nPress ENTER on your Orange Pi keyboard to START the demo...")
    input()
    
    print("\n>>> MOVING FORWARD (10 seconds)")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print(">>> STOPPING to sample Cold Water...")
    esp32.write(b"STOP\n")
    time.sleep(2) 
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"    [SENSOR DATA] Cold Water Temp: {temp_c} C")
    time.sleep(3)

    print("\n>>> MOVING FORWARD to Hot Bowl (10 seconds)")
    esp32.write(b"FWD\n")
    time.sleep(10)

    print(">>> STOPPING to sample Hot Water...")
    esp32.write(b"STOP\n")
    time.sleep(2)
    
    temp_c = get_temp_from_esp32(esp32)
    print(f"    [SENSOR DATA] Hot Water Temp: {temp_c} C")

    print("\n====================================")
    print("       Demonstration Complete!")
    print("====================================")

if __name__ == '__main__':
    main()
