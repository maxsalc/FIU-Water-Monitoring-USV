import serial
import time
import sys

# Automatically select port based on OS (Laptop vs Orange Pi)
if sys.platform.startswith('win'):
    RADIO_PORT = 'COM6'
else:
    RADIO_PORT = '/dev/ttyS7'

RADIO_BAUD = 9600

def read_config(ser):
    # E32 read config command is C1 C1 C1
    ser.write(b'\xC1\xC1\xC1')
    time.sleep(0.5)
    if ser.in_waiting >= 6:
        data = ser.read(6)
        return list(data)
    return None

def write_config(ser, config_bytes):
    # E32 write config permanent is C0 + 5 bytes
    ser.write(bytes(config_bytes))
    time.sleep(0.5)
    if ser.in_waiting >= 6:
        data = ser.read(6)
        return list(data)
    return None

def print_speed(sped_byte):
    baud_dict = {0:1200, 1:2400, 2:4800, 3:9600, 4:19200, 5:38400, 6:57600, 7:115200}
    air_dict = {0:0.3, 1:1.2, 2:2.4, 3:4.8, 4:9.6, 5:19.2, 6:19.2, 7:19.2}
    
    baud_bits = (sped_byte >> 3) & 0b111
    air_bits = sped_byte & 0b111
    
    print(f"  UART Baud Rate: {baud_dict.get(baud_bits, 'Unknown')} bps")
    print(f"  Air Data Rate:  {air_dict.get(air_bits, 'Unknown')} kbps")

def main():
    print("====================================")
    print("    E32-900T20D CONFIGURATOR        ")
    print("====================================")
    print(f"Using Port: {RADIO_PORT}")
    print("\nCRITICAL: Before continuing, you MUST physically connect BOTH")
    print("the M0 and M1 pins on the radio module to 3.3V.")
    print("This puts the module into 'Sleep/Command' Mode.")
    input("Press ENTER when M0 and M1 are connected to 3.3V...")
    
    try:
        ser = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
    except Exception as e:
        print(f"Error opening port: {e}")
        return

    print("\nReading current configuration from radio...")
    current_config = read_config(ser)
    
    if not current_config:
        print("[ERROR] No response from module. Are M0 and M1 definitely connected to 3.3V?")
        print("Double check your wiring and run again.")
        ser.close()
        return

    print("\n[CURRENT CONFIGURATION]")
    print(f"Raw Bytes: {[hex(b) for b in current_config]}")
    print_speed(current_config[3])
    
    # We want to change Air Data Rate to 19.2k (bits 0,1,2 = 101 in binary)
    # We keep UART Baud Rate the exact same (bits 3,4,5)
    # We keep Parity the exact same (bits 6,7)
    
    new_config = current_config.copy()
    new_config[0] = 0xC0 # Ensure it's a WRITE permanent command
    
    # Clear bottom 3 bits, then set to 5 (101 in binary)
    new_config[3] = (new_config[3] & 0b11111000) | 0b101
    
    print("\n[PROPOSED CONFIGURATION]")
    print(f"Raw Bytes: {[hex(b) for b in new_config]}")
    print_speed(new_config[3])
    
    print("\nDo you want to flash this new 19.2kbps configuration to the radio? (y/n)")
    choice = input("> ")
    if choice.lower() == 'y':
        print("Flashing...")
        verify = write_config(ser, new_config)
        if verify and verify == new_config:
            print("\n✅ [SUCCESS] Configuration saved successfully!")
            print("IMPORTANT: Move M0 and M1 back to GND before running your bridge scripts!")
        else:
            print("\n❌ [ERROR] Failed to verify configuration. Received:")
            print(verify)
    else:
        print("Aborted.")
        
    ser.close()

if __name__ == '__main__':
    main()
