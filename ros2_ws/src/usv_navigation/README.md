# usv_navigation

Handles high-level navigation logic.

## Current Status

This node subscribes to GPS and heading data and publishes placeholder motor commands.

## Future Work

- Receive waypoints from dashboard/telemetry system
- Calculate distance to waypoint
- Calculate desired heading
- Compare desired heading against IMU heading
- Publish motor commands to `/usv/motor_command`
