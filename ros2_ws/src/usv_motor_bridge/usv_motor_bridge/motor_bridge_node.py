import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MotorBridgeNode(Node):
    def __init__(self):
        super().__init__("motor_bridge_node")

        self.create_subscription(Twist, "/usv/motor_command", self.motor_callback, 10)

        self.get_logger().info("USV motor bridge started")
        self.get_logger().info("UART to ESP32 is not implemented yet. Printing commands only.")

    def motor_callback(self, msg):
        forward = msg.linear.x
        turn = msg.angular.z

        left_motor = forward - turn
        right_motor = forward + turn

        self.get_logger().info(
            f"Motor command placeholder: LEFT={left_motor:.2f}, RIGHT={right_motor:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = MotorBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
