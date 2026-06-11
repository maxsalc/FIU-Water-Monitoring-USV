# FIU Water Monitoring USV

Low-cost unmanned surface vehicle (USV) for GPS-guided water quality monitoring using ROS2, an Orange Pi, ESP32 motor control, LoRa telemetry, and environmental sensors.

---

# System Architecture

## Orange Pi Responsibilities

The Orange Pi runs Ubuntu 22.04 with ROS2 Humble and handles:

* GPS integration
* IMU integration
* Water-quality sensor integration
* ROS2 communication
* Navigation logic
* Telemetry/logging
* Dashboard communication

The Orange Pi interfaces directly with:

* GPS module
* IMU
* pH sensor
* turbidity sensor
* TDS/conductivity sensor
* water temperature probe

---

## ESP32 Responsibilities

The ESP32 is dedicated to motor control only.

Responsibilities:

* Receive motor commands from the Orange Pi over UART
* Generate PWM signals for motor drivers
* Control left/right propulsion motors
* Implement safety timeout behavior if commands stop arriving

---

## Dashboard Responsibilities

The dashboard is intended to run on a nearby operator laptop and will eventually provide:

* live telemetry display
* satellite map view
* current USV position
* waypoint selection
* mission status
* future teleoperation functionality

Current dashboard stack:

* Flask backend
* Leaflet map frontend

---

# ROS2 Workspace Structure

```text
ros2_ws/src/
├── usv_sensor_bridge/
├── usv_navigation/
├── usv_motor_bridge/
└── usv_bringup/
```

---

# ROS2 Package Descriptions

## usv_sensor_bridge

Publishes sensor data to ROS2 topics.

Current status:

* supports placeholder sensor values
* intended to later interface with real Orange Pi hardware

Published topics:

* `/usv/gps`
* `/usv/heading_deg`
* `/usv/water_temperature_c`
* `/usv/ph`
* `/usv/turbidity`
* `/usv/tds`
* `/usv/battery_voltage`

Configuration file:

```text
ros2_ws/src/usv_sensor_bridge/config/sensors.yaml
```

---

## usv_navigation

Handles high-level navigation logic.

Current status:

* subscribes to GPS and heading data
* publishes placeholder motor commands

Future work:

* waypoint navigation
* heading correction
* autonomous path following

---

## usv_motor_bridge

Bridges ROS2 motor commands to the ESP32.

Current status:

* receives motor commands from ROS2
* prints calculated left/right motor values

Future work:

* UART communication with ESP32
* motor safety timeout logic
* packet protocol implementation

---

## usv_bringup

Contains ROS2 launch files used to start the robot stack.

---

# Sensor Configuration

Sensor configuration is stored in:

```text
ros2_ws/src/usv_sensor_bridge/config/sensors.yaml
```

Current default behavior:

```yaml
use_placeholder_values: true
```

This allows the ROS2 stack to run without hardware attached.

To begin real hardware integration:

```yaml
use_placeholder_values: false
```

Then replace placeholder logic inside:

```text
sensor_bridge_node.py
```

with real sensor-reading code.

---

# Robot Startup Instructions

Target platform:

* Orange Pi
* Ubuntu 22.04 Jammy
* ROS2 Humble Hawksbill

---

## Build Workspace

From the repository root:

```bash
cd ros2_ws
colcon build
```

---

## Source ROS2 Workspace

```bash
source install/setup.bash
```

---

## Launch Robot Stack

```bash
ros2 launch usv_bringup robot.launch.py
```

This launches:

* sensor bridge node
* navigation node
* motor bridge node

---

# Testing ROS2 Topics

Open another terminal:

```bash
cd ros2_ws
source install/setup.bash
```

List topics:

```bash
ros2 topic list
```

Echo GPS topic:

```bash
ros2 topic echo /usv/gps
```

Echo pH topic:

```bash
ros2 topic echo /usv/ph
```

Echo water temperature:

```bash
ros2 topic echo /usv/water_temperature_c
```

Echo motor commands:

```bash
ros2 topic echo /usv/motor_command
```

---

# Current Development Status

The ROS2 stack currently supports:

* package structure
* launch system
* placeholder telemetry
* inter-node communication
* dashboard groundwork

Still in development:

* real sensor integration
* UART communication to ESP32
* waypoint navigation
* autonomous control
* LoRa telemetry integration
* final hull integration
* power system integration

---

# Power System Plan

Current planned architecture:

```text
12V battery
├── Motor drivers → 12V propulsion motors
└── 5V buck converter
    ├── Orange Pi
    ├── ESP32
    ├── sensors
    └── LoRa modules
```

Planned propulsion:

* dual differential drive
* independent left/right thrust control

---

# Planned Telemetry Architecture

```text
Sensors
↓
Orange Pi ROS2 Nodes
↓
Navigation + telemetry
↓
LoRa
↓
Operator dashboard laptop
```

---

# Future Navigation Workflow

Planned autonomous navigation loop:

```text
Current GPS position
+
Current heading
+
Target waypoint
↓
Heading error calculation
↓
Motor command generation
↓
ESP32 motor control
```

---

# Dashboard Goals

Planned dashboard functionality:

* live USV location
* satellite map view
* waypoint selection
* telemetry graphs
* mission logging
* future teleoperation controls

Current mapping stack:

* Leaflet
* OpenStreetMap / future satellite imagery support

---

