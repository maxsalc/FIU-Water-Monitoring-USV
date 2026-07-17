import serial
import time
import msvcrt
import sys

RADIO_PORT = 'COM6'
RADIO_BAUD = 9600
STATUS_QUERY_INTERVAL = 2.0  # Request telemetry every 2 seconds

def main():
    print("===========================================")
    print("      ASV GROUND STATION CONTROLLER")
    print("===========================================")
    print("Connecting to Radio...")
    
    try:
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1.0)
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
        # 1. READ Incoming Telemetry from Radio
        if radio.in_waiting > 0:
            try:
                line = radio.readline().decode('utf-8', errors='ignore').strip()
                if line and line.startswith("S:"):
                    print(f"\r[TELEMETRY] {line}                   ")
                    print("Send Command (W/A/S/D/SPACE): ", end="", flush=True)
            except Exception as e:
                pass

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
                radio.write(f"{msg}\n".encode('utf-8'))
                last_key = msg
                # Delay the next automatic telemetry query slightly to avoid collisions
                last_query_time = time.time() - (STATUS_QUERY_INTERVAL - 0.5)
                
        # 3. PERIODIC TELEMETRY QUERY (Master requests, Slave responds)
        current_time = time.time()
        if current_time - last_query_time >= STATUS_QUERY_INTERVAL:
            radio.write(b"STATUS\n")
            last_query_time = current_time
            
        time.sleep(0.01)

    print("\nExiting Ground Station.")

if __name__ == '__main__':
    main()
