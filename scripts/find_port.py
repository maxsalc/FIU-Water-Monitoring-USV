import serial
import time
import glob

def main():
    print("--- Orange Pi Loopback Port Finder ---")
    print("Make sure you have a single wire connecting Physical Pin 8 directly to Physical Pin 10.")
    print("Testing all available serial ports...\n")

    # Get all ttyS* and ttyUSB* ports
    ports = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUART*')
    
    found_port = None

    for port in ports:
        try:
            # Try to open the port
            s = serial.Serial(port, 9600, timeout=0.5)
            
            # Send a unique message
            test_msg = f"PING_{port}\n".encode('utf-8')
            s.write(test_msg)
            
            # Wait a tiny bit for it to loop back
            time.sleep(0.1)
            
            # Read whatever came back
            if s.in_waiting > 0:
                response = s.readline()
                if response == test_msg:
                    print(f"[SUCCESS] Found active loopback on: {port}")
                    found_port = port
            s.close()
        except Exception as e:
            # Port might be in use or permission denied, just skip
            pass

    if found_port:
        print(f"\n>>> Your exact port for Pins 8/10 is: {found_port} <<<")
        print("Update demo_controller.py to use this port!")
    else:
        print("\n[FAILED] Could not find any port that looped the signal back.")
        print("Please double check that the wire is bridging Pin 8 and Pin 10 tightly.")

if __name__ == '__main__':
    main()
