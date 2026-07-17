import serial
import time

RADIO_PORT = '/dev/ttyS7'
RADIO_BAUD = 9600

ESP32_PORT = '/dev/ttyUSB0'
ESP32_BAUD = 115200

def main():
    print("====================================")
    print("    ORANGE PI TELEMETRY BRIDGE      ")
    print("====================================")

    # 1. Connect to Radio
    try:
        print(f"Connecting to Radio on {RADIO_PORT}...")
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=0.1)
        print("[SUCCESS] Connected to Radio.")
    except Exception as e:
        print(f"[ERROR] Failed to open Radio: {e}")
        return

    # 2. Connect to ESP32
    try:
        print(f"Connecting to ESP32 on {ESP32_PORT}...")
        esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=0.1)
        # Linux specific serial reset fixes for ESP32
        esp32.setDTR(False)
        esp32.setRTS(False)
        print("[SUCCESS] Connected to ESP32.")
    except Exception as e:
        print(f"[ERROR] Failed to open ESP32: {e}")
        radio.close()
        return

    print("\n--- Wireless Bridge Active ---")
    print("Listening for Laptop commands and ESP32 telemetry...\n")

    try:
        while True:
            # A. DOWNSTREAM: Radio (Laptop) ➔ ESP32
            if radio.in_waiting > 0:
                radio_cmd = radio.readline().decode('utf-8', errors='ignore').strip()
                if radio_cmd:
                    print(f"[RADIO RECV] Command: {radio_cmd}")
                    
                    # Translate high-level command to ESP32 motor setpoints
                    esp_cmd = ""
                    if radio_cmd == "FWD":
                        esp_cmd = "M:200,200\n"
                    elif radio_cmd == "BWD":
                        esp_cmd = "M:-200,-200\n"
                    elif radio_cmd == "LEFT":
                        esp_cmd = "M:-150,150\n"
                    elif radio_cmd == "RIGHT":
                        esp_cmd = "M:150,-150\n"
                    elif radio_cmd == "STOP":
                        esp_cmd = "M:0,0\n"
                    
                    if esp_cmd:
                        esp32.write(esp_cmd.encode('utf-8'))
                        print(f"  └─► Forwarded to ESP32: {esp_cmd.strip()}")

            # B. UPSTREAM: ESP32 ➔ Radio (Laptop) & Local Screen
            if esp32.in_waiting > 0:
                esp_line = esp32.readline().decode('utf-8', errors='ignore').strip()
                if esp_line:
                    # If it's a telemetry packet
                    if esp_line.startswith("S:"):
                        print(f"[TELEMETRY] {esp_line}")
                        # Temporarily disabled radio transmission to prevent half-duplex RF collision
                        # radio.write(f"{esp_line}\n".encode('utf-8'))
                    else:
                        # Print generic debug logs locally
                        print(f"[ESP32 Debug] {esp_line}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping Wireless Bridge...")
    finally:
        radio.close()
        esp32.close()
        print("Serial ports closed.")

if __name__ == '__main__':
    main()
