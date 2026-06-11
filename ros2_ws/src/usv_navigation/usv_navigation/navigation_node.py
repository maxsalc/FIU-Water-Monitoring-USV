import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from sensor_msgs.msg import NavSatFix


class NavigationNode(Node):
    def __init__(self):
        super().__init__("navigation_node")

        self.latest_gps = None
        self.latest_heading = None

        self.motor_pub = self.create_publisher(Twist, "/usv/motor_command", 10)

        self.create_subscription(NavSatFix, "/usv/gps", self.gps_callback, 10)
        self.create_subscription(Float32, "/usv/heading_deg", self.heading_callback, 10)

        self.timer = self.create_timer(1.0, self.publish_test_motor_command)

        self.get_logger().info("USV navigation node started")

    def gps_callback(self, msg):
        self.latest_gps = msg

    def heading_callback(self, msg):
        self.latest_heading = msg.data

    def publish_test_motor_command(self):
        cmd = Twist()

        # Placeholder command for integration testing.
        # Later this will be calculated from GPS waypoint + heading error.
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        self.motor_pub.publish(cmd)

        if self.latest_gps is not None:
            self.get_logger().info(
                f"GPS lat={self.latest_gps.latitude}, lon={self.latest_gps.longitude}, heading={self.latest_heading}"
            )


def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
