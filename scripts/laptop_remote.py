import serial
import time
import msvcrt
import sys

RADIO_PORT = 'COM4'
RADIO_BAUD = 9600

def main():
    print("===========================================")
    print("      ASV GROUND STATION CONTROLLER")
    print("===========================================")
    print("Connecting to Radio...")
    
    try:
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
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
    
    print("Ready to send commands... (Make sure this terminal is selected!)")
    
    last_key = None
    
    while True:
        if msvcrt.kbhit():
            key_bytes = msvcrt.getch()
            # Handle special keys (arrows, esc)
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

            if msg and msg != last_key: # Only print/send if it changed (prevents spamming if held down)
                print(f"Broadcasting: {msg}")
                radio.write(f"{msg}\n".encode('utf-8'))
                last_key = msg
                
        time.sleep(0.01)

    print("\nExiting Ground Station.")

if __name__ == '__main__':
    main()
