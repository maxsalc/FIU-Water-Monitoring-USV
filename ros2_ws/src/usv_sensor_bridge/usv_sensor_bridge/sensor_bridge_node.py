import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import NavSatFix


class SensorBridgeNode(Node):
    def __init__(self):
        super().__init__("sensor_bridge_node")

        self.declare_parameter("use_placeholder_values", True)

        self.declare_parameter("placeholder_latitude", 25.7560)
        self.declare_parameter("placeholder_longitude", -80.3750)
        self.declare_parameter("placeholder_heading_deg", 90.0)
        self.declare_parameter("placeholder_temperature_c", 27.4)
        self.declare_parameter("placeholder_ph", 7.1)
        self.declare_parameter("placeholder_turbidity", 320.0)
        self.declare_parameter("placeholder_tds", 510.0)
        self.declare_parameter("placeholder_battery_voltage", 11.8)

        self.gps_pub = self.create_publisher(NavSatFix, "/usv/gps", 10)
        self.heading_pub = self.create_publisher(Float32, "/usv/heading_deg", 10)
        self.temp_pub = self.create_publisher(Float32, "/usv/water_temperature_c", 10)
        self.ph_pub = self.create_publisher(Float32, "/usv/ph", 10)
        self.turbidity_pub = self.create_publisher(Float32, "/usv/turbidity", 10)
        self.tds_pub = self.create_publisher(Float32, "/usv/tds", 10)
        self.battery_pub = self.create_publisher(Float32, "/usv/battery_voltage", 10)

        self.timer = self.create_timer(1.0, self.publish_sensor_data)

        self.get_logger().info("USV sensor bridge started")

    def publish_sensor_data(self):
        use_placeholder = self.get_parameter("use_placeholder_values").value

        if use_placeholder:
            self.publish_placeholder_data()
        else:
            self.get_logger().warn(
                "Real sensor mode selected, but hardware readers are not implemented yet."
            )

    def publish_placeholder_data(self):
        gps = NavSatFix()
        gps.latitude = self.get_parameter("placeholder_latitude").value
        gps.longitude = self.get_parameter("placeholder_longitude").value
        gps.altitude = 0.0
        self.gps_pub.publish(gps)

        self.heading_pub.publish(Float32(data=self.get_parameter("placeholder_heading_deg").value))
        self.temp_pub.publish(Float32(data=self.get_parameter("placeholder_temperature_c").value))
        self.ph_pub.publish(Float32(data=self.get_parameter("placeholder_ph").value))
        self.turbidity_pub.publish(Float32(data=self.get_parameter("placeholder_turbidity").value))
        self.tds_pub.publish(Float32(data=self.get_parameter("placeholder_tds").value))
        self.battery_pub.publish(Float32(data=self.get_parameter("placeholder_battery_voltage").value))

        self.get_logger().info("Published placeholder sensor data")


def main(args=None):
    rclpy.init(args=args)
    node = SensorBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
