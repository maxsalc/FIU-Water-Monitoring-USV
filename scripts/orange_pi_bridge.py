import serial
import time

RADIO_PORT = '/dev/ttyS7'
RADIO_BAUD = 9600

ESP32_PORT = '/dev/ttyUSB0'
ESP32_BAUD = 115200

class NonBlockingSerialReader:
    def __init__(self, ser_port):
        self.ser = ser_port
        self.buffer = ""

    def readline(self):
        # 1. Check if we already have a full line in our local buffer
        if '\n' in self.buffer:
            parts = self.buffer.split('\n', 1)
            line = parts[0].strip()
            self.buffer = parts[1]
            return line

        # 2. Read new bytes if they are waiting
        if self.ser.in_waiting > 0:
            raw = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
            self.buffer += raw
            if '\n' in self.buffer:
                parts = self.buffer.split('\n', 1)
                line = parts[0].strip()
                self.buffer = parts[1]
                return line
        return None

def main():
    print("====================================")
    print("    ORANGE PI TELEMETRY BRIDGE      ")
    print("====================================")

    # 1. Connect to Radio
    try:
        print(f"Connecting to Radio on {RADIO_PORT}...")
        # Open with 0 timeout to make reads completely non-blocking
        radio_ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=0)
        radio = NonBlockingSerialReader(radio_ser)
        print("[SUCCESS] Connected to Radio.")
    except Exception as e:
        print(f"[ERROR] Failed to open Radio: {e}")
        return

    # 2. Connect to ESP32
    try:
        print(f"Connecting to ESP32 on {ESP32_PORT}...")
        esp32_ser = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=0)
        esp32 = NonBlockingSerialReader(esp32_ser)
        # Linux specific serial reset fixes for ESP32
        esp32_ser.setDTR(False)
        esp32_ser.setRTS(False)
        print("[SUCCESS] Connected to ESP32.")
    except Exception as e:
        print(f"[ERROR] Failed to open ESP32: {e}")
        radio_ser.close()
        return

    print("\n--- Wireless Bridge Active (Non-Blocking Mode) ---")
    print("Listening for Laptop commands and ESP32 telemetry...\n")

    latest_telemetry = ""

    last_broadcast_time = time.time()

    try:
        while True:
            # A. DOWNSTREAM: Radio (Laptop) ➔ ESP32 / Command Parser
            radio_cmd = radio.readline()
            if radio_cmd:
                # If laptop is sending a motor command
                if radio_cmd != "STATUS":
                    print(f"[RADIO RECV] Command: {radio_cmd}")
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
                        esp32_ser.write(esp_cmd.encode('utf-8'))
                        print(f"  └─► Forwarded to ESP32: {esp_cmd.strip()}")

            # B. UPSTREAM: ESP32 ➔ Local Cache & Screen
            esp_line = esp32.readline()
            if esp_line:
                if esp_line.startswith("S:"):
                    # Cache the latest telemetry locally
                    latest_telemetry = esp_line
                    print(f"[LOCAL TELEMETRY] {esp_line}")
                else:
                    # Print generic debug logs locally
                    print(f"[ESP32 Debug] {esp_line}")

            # C. BROADCAST TELEMETRY AUTOMATICALLY (Every 2 seconds)
            current_time = time.time()
            if current_time - last_broadcast_time >= 2.0:
                if latest_telemetry:
                    radio_ser.write(f"{latest_telemetry}\n".encode('utf-8'))
                    print(f"[RADIO] Auto-Broadcasted Telemetry")
                last_broadcast_time = current_time

            time.sleep(0.005) # Run the loop extremely fast (200Hz)

    except KeyboardInterrupt:
        print("\nStopping Wireless Bridge...")
    finally:
        radio_ser.close()
        esp32_ser.close()
        print("Serial ports closed.")

if __name__ == '__main__':
    main()
