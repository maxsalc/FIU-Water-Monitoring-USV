import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    sensor_config = os.path.join(
        get_package_share_directory("usv_sensor_bridge"),
        "config",
        "sensors.yaml",
    )

    return LaunchDescription([
        Node(
            package="usv_sensor_bridge",
            executable="sensor_bridge_node",
            name="sensor_bridge_node",
            output="screen",
            parameters=[sensor_config],
        ),
        Node(
            package="usv_navigation",
            executable="navigation_node",
            name="navigation_node",
            output="screen",
        ),
        Node(
            package="usv_motor_bridge",
            executable="motor_bridge_node",
            name="motor_bridge_node",
            output="screen",
        ),
    ])
