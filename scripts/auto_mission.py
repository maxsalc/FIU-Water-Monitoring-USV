import serial
import time
import sys

RADIO_PORT = 'COM6'
RADIO_BAUD = 9600

class NonBlockingSerialReader:
    def __init__(self, ser_port):
        self.ser = ser_port
        self.buffer = ""

    def readline(self):
        if '\n' in self.buffer:
            parts = self.buffer.split('\n', 1)
            line = parts[0].strip()
            self.buffer = parts[1]
            return line

        if self.ser.in_waiting > 0:
            raw = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
            self.buffer += raw
            if '\n' in self.buffer:
                parts = self.buffer.split('\n', 1)
                line = parts[0].strip()
                self.buffer = parts[1]
                return line
        return None

def send_command(radio_ser, cmd):
    print(f"\n[MISSION CONTROL] ➔ Executing Command: {cmd}")
    radio_ser.write(f"{cmd}\n".encode('utf-8'))

def listen_telemetry(radio, duration_sec):
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        line = radio.readline()
        if line and line.startswith("S:"):
            raw_data = line[2:].split(',')
            if len(raw_data) >= 4:
                temp = raw_data[0]
                salinity = raw_data[1]
                lat = raw_data[-2]
                lng = raw_data[-1]
                print(f"  └─► [LIVE TELEMETRY] Temp: {temp}°C | Salinity: {salinity} ppm | Lat: {lat} | Lng: {lng}")
            else:
                print(f"  └─► [LIVE TELEMETRY] {line}")
        time.sleep(0.01)

def main():
    print("===========================================")
    print("   ASV AUTONOMOUS PRE-PROGRAMMED MISSION   ")
    print("===========================================")
    print(f"Connecting to Ground Station Radio on {RADIO_PORT}...")
    
    try:
        radio_ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=0)
        radio = NonBlockingSerialReader(radio_ser)
        print("[SUCCESS] Radio connected!")
    except Exception as e:
        print(f"[ERROR] Failed to open {RADIO_PORT}: {e}")
        return

    print("\nStarting Pre-Programmed Autonomous Path in 3 seconds...")
    listen_telemetry(radio, 3.0)

    # --- AUTONOMOUS MANEUVER SEQUENCE ---
    sequence = [
        ("BOTH MOTORS 100% FORWARD", "FWD", 3.0),
        ("TURN LEFT (RIGHT MOTOR 100%)", "LEFT", 2.0),
        ("BOTH MOTORS 100% FORWARD", "FWD", 3.0),
        ("TURN RIGHT (LEFT MOTOR 100%)", "RIGHT", 2.0),
        ("BOTH MOTORS 100% REVERSE", "BWD", 2.0),
        ("STOP MOTORS & SAMPLE WATER", "STOP", 5.0)
    ]

    try:
        for step_name, command, duration in sequence:
            print(f"\n>>> STEP: {step_name} <<<")
            send_command(radio_ser, command)
            listen_telemetry(radio, duration)

        print("\n===========================================")
        print("   ✅ MISSION COMPLETE - ALL STOPS DONE    ")
        print("===========================================")

    except KeyboardInterrupt:
        print("\n[EMERGENCY STOP] Mission interrupted by user!")
        send_command(radio_ser, "STOP")
    finally:
        radio_ser.close()
        print("Ground Station Closed.")

if __name__ == '__main__':
    main()
