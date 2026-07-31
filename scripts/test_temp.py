import serial
import time

ESP32_PORT = '/dev/ttyUSB0'
ESP32_BAUD = 115200

def main():
    print("====================================")
    print("    ESP32 TEMPERATURE MONITOR       ")
    print("====================================")
    print(f"Opening {ESP32_PORT} at {ESP32_BAUD} baud...")
    
    try:
        esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
        # Prevent ESP32 from resetting on connection (Linux DTR/RTS issue)
        esp32.setDTR(False)
        esp32.setRTS(False)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return

    print("\nListening for temperature data... (Press Ctrl+C to stop)\n")
    try:
        while True:
            if esp32.in_waiting > 0:
                line = esp32.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"[ESP32] {line}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        esp32.close()

if __name__ == '__main__':
    main()
