# my_bot

Autonomous differential-drive robot · ROS 2 Jazzy · Gazebo Harmonic · Nav2

<p align="center">
  <img src="docs/robot.jpg" width="320" alt="The physical robot: Raspberry Pi 4, Arduino Nano, L298N motor driver and battery pack in its chassis">
</p>

A three-wheeled mobile robot that maps a room with SLAM and navigates it autonomously with Nav2. One package covers the robot model, the Gazebo simulation and the hardware bring-up, and a single launch argument switches between the simulated and the physical robot.

- **Robot model:** URDF/xacro with a 360° lidar and a front camera
- **Control:** ros2_control `diff_drive_controller`, shared by simulation and hardware (Raspberry Pi 4 + Arduino Nano)
- **Mapping and navigation:** slam_toolbox, AMCL, NavFn planner, MPPI controller

**Status:** SLAM and autonomous navigation work in simulation. The physical robot is assembled and its hardware interface is in place; encoder calibration and lidar integration are in progress before it can navigate on its own.

## Quick start

```bash
cd ~/dev_ws/src && git clone https://github.com/merpe24/my_bot.git
cd ~/dev_ws && colcon build --symlink-install && source install/setup.bash

ros2 launch my_bot launch_sim.launch.py      # simulation
ros2 launch my_bot launch_robot.launch.py    # physical robot
```

SLAM, Nav2 and `twist_mux` configurations are in `config/`, and the saved map of the test room is in `maps/`.

Based on the [Articulated Robotics](https://articulatedrobotics.xyz/) series, ported to Jazzy and Gazebo Harmonic. Apache-2.0.
