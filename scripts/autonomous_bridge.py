import serial
import time
import threading

RADIO_PORT = '/dev/ttyS7'
RADIO_BAUD = 9600

ESP32_PORT = '/dev/ttyUSB0'
ESP32_BAUD = 115200

# Global state
latest_telemetry = ""
mission_running = False

def robust_write(ser, text):
    """Sends strings byte-by-byte to prevent UART clock-drift corruption on SBCs"""
    for char in text:
        ser.write(char.encode('utf-8'))
        ser.flush()
        time.sleep(0.02) # 20ms delay ensures we do not overrun the LoRa module's slow air data rate

def run_mission(esp32_ser, radio_ser):
    global mission_running, latest_telemetry
    mission_running = True
    
    print("\n[AUTONOMY] Starting Mission Sequence...")
    robust_write(radio_ser, "ACK: Mission Started\n")
    
    # Sequence: Forward, Left, Forward, Right, Right, Down(Bwd), Stop, Sample
    sequence = [
        ("FWD", "M:200,200\n", 2.0),
        ("LEFT", "M:-150,150\n", 1.0),
        ("FWD", "M:200,200\n", 2.0),
        ("RIGHT", "M:150,-150\n", 1.0),
        ("RIGHT", "M:150,-150\n", 1.0),
        ("BWD", "M:-200,-200\n", 2.0),
        ("STOP", "M:0,0\n", 2.0) # Wait 2 seconds for water to settle
    ]
    
    for name, cmd, duration in sequence:
        print(f"[AUTONOMY] Executing: {name}")
        esp32_ser.write(cmd.encode('utf-8'))
        time.sleep(duration)
        
    print("[AUTONOMY] Mission Navigation Complete. Sampling Sensors...")
    
    # At this point, the main thread is constantly updating latest_telemetry in the background
    result = latest_telemetry if latest_telemetry else "S:NO_DATA"
    print(f"[AUTONOMY] Findings: {result}")
    
    # Transmit to Laptop
    robust_write(radio_ser, f"MISSION_COMPLETE: {result}\n")
    
    mission_running = False

def main():
    global latest_telemetry, mission_running
    print("====================================")
    print("   ORANGE PI AUTONOMOUS BRIDGE      ")
    print("====================================")

    try:
        radio_ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=0)
        print(f"[SUCCESS] Connected to Radio on {RADIO_PORT}.")
    except Exception as e:
        print(f"[ERROR] Failed to open Radio: {e}")
        return

    try:
        esp32_ser = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=0)
        esp32_ser.setDTR(False)
        esp32_ser.setRTS(False)
        print(f"[SUCCESS] Connected to ESP32 on {ESP32_PORT}.")
    except Exception as e:
        print(f"[ERROR] Failed to open ESP32: {e}")
        radio_ser.close()
        return

    print("\nListening for Mission Dispatch...\n")

    try:
        esp32_buffer = ""
        radio_buffer = ""
        
        while True:
            # 1. Read Radio for Start Command
            if radio_ser.in_waiting > 0:
                radio_buffer += radio_ser.read(radio_ser.in_waiting).decode('utf-8', errors='ignore')
                if '\n' in radio_buffer:
                    parts = radio_buffer.split('\n', 1)
                    radio_cmd = parts[0].strip()
                    radio_buffer = parts[1]
                    
                    if radio_cmd == "START_MISSION" and not mission_running:
                        print(f"[RADIO RECV] {radio_cmd}")
                        # Launch mission in a background thread so we can keep reading telemetry
                        threading.Thread(target=run_mission, args=(esp32_ser, radio_ser), daemon=True).start()

            # 2. Continually Read ESP32 Telemetry in the background
            if esp32_ser.in_waiting > 0:
                esp32_buffer += esp32_ser.read(esp32_ser.in_waiting).decode('utf-8', errors='ignore')
                if '\n' in esp32_buffer:
                    parts = esp32_buffer.split('\n', 1)
                    esp_line = parts[0].strip()
                    esp32_buffer = parts[1]
                    
                    if esp_line.startswith("S:"):
                        latest_telemetry = esp_line
                        # We do not print it here to keep the console clean during the mission

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        radio_ser.close()
        esp32_ser.close()

if __name__ == '__main__':
    main()
