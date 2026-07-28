import serial
import time
import msvcrt
import sys

RADIO_PORT = 'COM6'
RADIO_BAUD = 9600
STATUS_QUERY_INTERVAL = 2.0  # Request telemetry every 2 seconds

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

def main():
    print("===========================================")
    print("      ASV GROUND STATION CONTROLLER")
    print("===========================================")
    print("Connecting to Radio...")
    
    try:
        radio_ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=0)
        radio = NonBlockingSerialReader(radio_ser)
    except Exception as e:
        print(f"Failed to open {RADIO_PORT}: {e}")
        return

    print("\n[SUCCESS] Radio connected!")
    print("\n--- CONTROLS ---")
    print(" W : Move Forward")
    print(" S : Move Backward")
    print(" A : Turn Left")
    print(" D : Turn Right")
    print(" SPACE : Stop Motors")
    print(" ESC : Exit")
    print("----------------")
    
    print("Ready to send/receive... (Terminal must be selected!)")
    
    last_key = None
    last_query_time = 0
    
    while True:
        # 1. READ Incoming Telemetry from Radio (Non-blocking)
        line = radio.readline()
        if line:
            if line.startswith("S:"):
                raw_data = line[2:].split(',')
                if len(raw_data) == 4:
                    temp, salinity, lat, lng = raw_data[0], raw_data[1], raw_data[2], raw_data[3]
                    print(f"\r[TELEMETRY] Temp: {temp}°C | Salinity: {salinity} ppm | Lat: {lat} | Lng: {lng}                   ")
                else:
                    print(f"\r[TELEMETRY] {line}                   ")
                print("Send Command (W/A/S/D/SPACE): ", end="", flush=True)

        # 2. WRITE Outgoing Keyboard Commands to Radio
        if msvcrt.kbhit():
            key_bytes = msvcrt.getch()
            if key_bytes == b'\x1b': # ESC
                break
                
            try:
                key = key_bytes.decode('utf-8').upper()
            except:
                continue

            msg = ""
            if key == 'W':
                msg = "FWD"
            elif key == 'S':
                msg = "BWD"
            elif key == 'A':
                msg = "LEFT"
            elif key == 'D':
                msg = "RIGHT"
            elif key == ' ':
                msg = "STOP"

            if msg and msg != last_key:
                print(f"\nBroadcasting Command: {msg}")
                radio_ser.write(f"{msg}\n".encode('utf-8'))
                last_key = msg
                # Delay the next automatic status query slightly to keep the link clear
                last_query_time = time.time() - (STATUS_QUERY_INTERVAL - 0.5)
                
        # 3. NO MORE POLLING - Just listen passively for telemetry
        time.sleep(0.005) # Run loop extremely fast

    radio_ser.close()
    print("\nExiting Ground Station.")

if __name__ == '__main__':
    main()
