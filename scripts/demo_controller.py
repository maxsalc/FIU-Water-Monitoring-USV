import serial
import time
import glob
import os

# Configuration (Adjust these ports if needed)
ESP32_PORT = '/dev/ttyUSB0'   # Usually ttyUSB0 or ttyACM0 when plugged via USB
RADIO_PORT = '/dev/ttyS3'     # UART3 on Orange Pi
BAUD_RATE = 115200

def get_temp_sensor_file():
    base_dir = '/sys/bus/w1/devices/'
    try:
        device_folder = glob.glob(base_dir + '28*')[0]
        return device_folder + '/w1_slave'
    except IndexError:
        print("ERROR: Could not find DS18B20 sensor. Check wiring and 1-Wire setting.")
        return None

def read_temp_c(device_file):
    if not device_file:
        return -999.0
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return -999.0
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            return float(temp_string) / 1000.0
    except Exception as e:
        print(f"Failed to read temp: {e}")
    return -999.0

def main():
    print("Starting Orange Pi Demo Controller...")
    
    # Initialize Serials
    try:
        esp32 = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to ESP32 on {ESP32_PORT}")
    except Exception as e:
        print(f"Failed to connect to ESP32: {e}")
        return

    try:
        radio = serial.Serial(RADIO_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Radio on {RADIO_PORT}")
    except Exception as e:
        print(f"Failed to connect to Radio: {e}")
        return

    temp_file = get_temp_sensor_file()

    print("\nWaiting for 'START' command from Laptop via Radio...")
    while True:
        if radio.in_waiting > 0:
            msg = radio.readline().decode('utf-8').strip()
            if msg == "START":
                print("Start command received! Beginning 40-second demonstration.")
                break
        time.sleep(0.1)

    # --- THE CHOREOGRAPHY ---
    
    # 1. Move to Cold Bowl (10s)
    print("Moving Forward...")
    esp32.write(b"FWD\n")
    time.sleep(10)

    # 2. Stop and Sample Cold (5s)
    print("Stopping to sample Cold Water...")
    esp32.write(b"STOP\n")
    time.sleep(2) # let water settle
    temp_c = read_temp_c(temp_file)
    print(f"Cold Temp read: {temp_c} C")
    radio.write(f"COLD_TEMP: {temp_c:.2f} C\n".encode('utf-8'))
    time.sleep(3)

    # 3. Move to Hot Bowl (10s)
    print("Moving Forward to Hot Bowl...")
    # You could insert a turn here if you wanted: esp32.write(b"LEFT\n"); time.sleep(2)
    esp32.write(b"FWD\n")
    time.sleep(10)

    # 4. Stop and Sample Hot (5s)
    print("Stopping to sample Hot Water...")
    esp32.write(b"STOP\n")
    time.sleep(2)
    temp_c = read_temp_c(temp_file)
    print(f"Hot Temp read: {temp_c} C")
    radio.write(f"HOT_TEMP: {temp_c:.2f} C\n".encode('utf-8'))
    time.sleep(3)

    print("Demonstration Complete!")

if __name__ == '__main__':
    main()
