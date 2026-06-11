# usv_motor_bridge

Bridges ROS2 motor commands to the ESP32 motor controller.

## Current Status

This node subscribes to `/usv/motor_command` and prints left/right motor values.

## Future Work

- Open UART serial connection to ESP32
- Send motor packets to ESP32
- Add heartbeat/timeout safety behavior
- Confirm ESP32 stops motors if commands stop arriving
