import serial
import time
import sys

# Try to import Orange Pi GPIO
try:
    import OPi.GPIO as GPIO
except ImportError:
    print("CRITICAL ERROR: OPi.GPIO library is missing!")
    print("Please run: sudo pip3 install OPi.GPIO")
    sys.exit(1)

RADIO_PORT = '/dev/ttyS7'
RADIO_BAUD = 9600

# We will use the Physical Pin numbers on the 40-pin header
# Wire the L298N IN1-IN4 to these physical pins:
IN1 = 11
IN2 = 13
IN3 = 15
IN4 = 16

def stop_motors():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def move_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def move_backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

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

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    
    stop_motors()
    
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
        GPIO.cleanup()

if __name__ == '__main__':
    main()
