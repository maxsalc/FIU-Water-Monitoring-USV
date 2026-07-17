import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Twist
import serial
import threading

class SensorBridgeNode(Node):
    def __init__(self):
        super().__init__("hardware_bridge_node")

        # Serial Configuration
        self.serial_port = '/dev/ttyUSB0'
        self.baud_rate = 115200
        
        try:
            self.esp32 = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            # Linux PySerial fixes for ESP32
            self.esp32.setDTR(False)
            self.esp32.setRTS(False)
            self.get_logger().info(f"Successfully connected to ESP32 on {self.serial_port}")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to ESP32: {e}")
            self.esp32 = None

        # --- PUBLISHERS (Upstream Telemetry) ---
        self.temp_pub = self.create_publisher(Float32, "/usv/water_temperature_c", 10)
        self.ph_pub = self.create_publisher(Float32, "/usv/ph", 10)
        self.salinity_pub = self.create_publisher(Float32, "/usv/salinity", 10)
        self.turbidity_pub = self.create_publisher(Float32, "/usv/turbidity", 10)
        self.visibility_pub = self.create_publisher(Float32, "/usv/visibility", 10)
        
        # (Placeholders for features not yet on ESP32)
        self.gps_pub = self.create_publisher(NavSatFix, "/usv/gps", 10)
        self.heading_pub = self.create_publisher(Float32, "/usv/heading_deg", 10)
        self.battery_pub = self.create_publisher(Float32, "/usv/battery_voltage", 10)

        # --- SUBSCRIBERS (Downstream Commands) ---
        self.motor_sub = self.create_subscription(
            Twist, 
            "/usv/motor_command", 
            self.motor_callback, 
            10
        )

        # Fast timer to constantly read the serial buffer
        self.timer = self.create_timer(0.05, self.read_serial_data)

    def motor_callback(self, msg):
        if not self.esp32:
            return

        # Simple skid-steer math based on standard Twist
        forward = msg.linear.x * 255.0  # Assuming Twist is -1.0 to 1.0
        turn = msg.angular.z * 255.0

        left_motor = int(forward - turn)
        right_motor = int(forward + turn)
        
        # Constrain to 8-bit PWM limits (-255 to 255)
        left_motor = max(min(left_motor, 255), -255)
        right_motor = max(min(right_motor, 255), -255)

        command_str = f"M:{left_motor},{right_motor}\n"
        
        try:
            self.esp32.write(command_str.encode('utf-8'))
            self.get_logger().debug(f"Sent to ESP32: {command_str.strip()}")
        except Exception as e:
            self.get_logger().error(f"Serial write error: {e}")

    def read_serial_data(self):
        if not self.esp32:
            return

        try:
            while self.esp32.in_waiting > 0:
                line = self.esp32.readline().decode('utf-8', errors='ignore').strip()
                
                # Check if it's a Sensor telemetry packet
                if line.startswith("S:"):
                    # Remove "S:" and split by commas
                    data = line[2:].split(',')
                    
                    if len(data) >= 5:
                        try:
                            # S:temp,pH,salinity,turbidity,visibility
                            self.temp_pub.publish(Float32(data=float(data[0])))
                            self.ph_pub.publish(Float32(data=float(data[1])))
                            self.salinity_pub.publish(Float32(data=float(data[2])))
                            self.turbidity_pub.publish(Float32(data=float(data[3])))
                            self.visibility_pub.publish(Float32(data=float(data[4])))
                            
                            self.get_logger().info(f"Published Telemetry: Temp={data[0]}C, pH={data[1]}")
                        except ValueError:
                            self.get_logger().warn(f"Failed to parse float from ESP32 data: {line}")
                
                elif line:
                    # Print any other debug messages from ESP32
                    self.get_logger().info(f"[ESP32 Debug] {line}")
                    
        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SensorBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
