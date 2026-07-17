import serial
import time

RADIO_PORT = 'COM6'
RADIO_BAUD = 9600

def main():
    print("===========================================")
    print("      ASV MISSION DISPATCH (Ground Station)")
    print("===========================================")
    
    try:
        radio_ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
    except Exception as e:
        print(f"Failed to open {RADIO_PORT}: {e}")
        return

    print("[SUCCESS] Radio connected!\n")
    print("Dispatching autonomous mission to ASV...")
    
    # Send mission start command
    radio_ser.write(b"START_MISSION\n")
    
    print("\nMission dispatched! Waiting for ASV to navigate and report back...\n")
    
    try:
        while True:
            if radio_ser.in_waiting > 0:
                line = radio_ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if "MISSION_COMPLETE" in line:
                        print(f"\n✅ [ASV REPORT] {line}")
                        break
                    else:
                        print(f"[ASV RADIO] {line}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
        
    radio_ser.close()
    print("\nMission Dispatcher closed.")

if __name__ == '__main__':
    main()
