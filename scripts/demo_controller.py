import serial
import time
import os

RADIO_PORT = '/dev/ttyS7'
RADIO_BAUD = 9600

# We will use the 'wPi' pin numbers mapped to Physical Pins 11, 13, 15, 16
# based on the Orange Pi 4 Pro 'gpio readall' table:
IN1 = 5  # Physical Pin 11
IN2 = 7  # Physical Pin 13
IN3 = 8  # Physical Pin 15
IN4 = 9  # Physical Pin 16

def stop_motors():
    os.system(f"gpio write {IN1} 0")
    os.system(f"gpio write {IN2} 0")
    os.system(f"gpio write {IN3} 0")
    os.system(f"gpio write {IN4} 0")

def move_forward():
    os.system(f"gpio write {IN1} 1")
    os.system(f"gpio write {IN2} 0")
    os.system(f"gpio write {IN3} 1")
    os.system(f"gpio write {IN4} 0")

def move_backward():
    os.system(f"gpio write {IN1} 0")
    os.system(f"gpio write {IN2} 1")
    os.system(f"gpio write {IN3} 0")
    os.system(f"gpio write {IN4} 1")

def turn_left():
    os.system(f"gpio write {IN1} 0")
    os.system(f"gpio write {IN2} 1")
    os.system(f"gpio write {IN3} 1")
    os.system(f"gpio write {IN4} 0")

def turn_right():
    os.system(f"gpio write {IN1} 1")
    os.system(f"gpio write {IN2} 0")
    os.system(f"gpio write {IN3} 0")
    os.system(f"gpio write {IN4} 1")

def setup_gpio():
    print("Setting up GPIO pins using WiringOP...")
    os.system(f"gpio mode {IN1} out")
    os.system(f"gpio mode {IN2} out")
    os.system(f"gpio mode {IN3} out")
    os.system(f"gpio mode {IN4} out")
    stop_motors()

def main():
    print("===========================================")
    print("      ASV ORANGE PI MOTOR CONTROLLER")
    print("===========================================")
    
    try:
        radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
        print(f"Connected to Radio on {RADIO_PORT}")
    except Exception as e:
        print(f"Failed to connect to Radio: {e}")
        return

    setup_gpio()
    
    print("\n[SUCCESS] Hardware initialized. Listening for radio commands...")

    try:
        while True:
            if radio.in_waiting > 0:
                msg = radio.readline().decode('utf-8', errors='ignore').strip()
                
                if "FWD" in msg:
                    print("Executing: FORWARD")
                    move_forward()
                elif "BWD" in msg:
                    print("Executing: BACKWARD")
                    move_backward()
                elif "LEFT" in msg:
                    print("Executing: TURN LEFT")
                    turn_left()
                elif "RIGHT" in msg:
                    print("Executing: TURN RIGHT")
                    turn_right()
                elif "STOP" in msg:
                    print("Executing: STOP")
                    stop_motors()
                    
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        stop_motors()

if __name__ == '__main__':
    main()
