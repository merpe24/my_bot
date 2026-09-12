# my_bot

Autonomous three-wheeled mobile robot — ROS 2 Jazzy, Gazebo Harmonic, Nav2.

A differential-drive robot (two driven wheels and a passive caster) that maps a room with SLAM and then navigates it autonomously. This package holds the robot description, the simulation, the navigation configuration and the bring-up for the physical robot. A single launch argument, `sim_mode`, selects either the Gazebo hardware plugin or the Arduino serial driver, so simulation and hardware run the same controllers and the same configuration.

The robot is modelled in URDF/xacro with a 360° lidar and a front camera. Motion goes through `ros2_control`: `diff_drive_controller` takes velocity commands and drives either `gz_ros2_control` in simulation or an Arduino Nano over USB serial on the real robot. Mapping uses `slam_toolbox` in online asynchronous mode. Navigation uses Nav2 with AMCL localization on the saved map, the NavFn global planner and the MPPI controller, with `twist_mux` arbitrating between Nav2 and keyboard teleop so a human can always take over.

**Status.** Mapping and autonomous goal navigation both work in simulation; the map of the test room is saved in `maps/`. On the physical robot the `ros2_control` hardware interface builds and runs, but the encoder resolution still has to be calibrated and the lidar driver is not integrated, so the robot has not navigated autonomously yet. Two open issues in simulation: MPPI runs at roughly 6.5 Hz against a 20 Hz target, and wheel slip drifts the odometry about 1 m per lap of the room, which AMCL corrects globally but which costs goal accuracy.

<!-- Demo: a GIF of Nav2 driving the robot in Gazebo/RViz belongs here -->

## Hardware

Raspberry Pi 4 (8 GB) · Arduino Nano running [ROSArduinoBridge](https://github.com/joshnewans/ros_arduino_bridge) firmware · L298N motor driver · 2 × JGB37-520 333 RPM motors with quadrature encoders · YDLIDAR X3 · USB webcam.

Simulated model: 0.40 × 0.30 × 0.15 m chassis, 0.05 m wheel radius, 0.35 m wheel separation, 360-sample lidar at 10 Hz (0.3–12 m).

## Running it

Requires Ubuntu 24.04 and ROS 2 Jazzy.

```bash
sudo apt install ros-jazzy-ros-gz ros-jazzy-gz-ros2-control ros-jazzy-ros2-controllers \
  ros-jazzy-xacro ros-jazzy-slam-toolbox ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-twist-mux ros-jazzy-teleop-twist-keyboard

mkdir -p ~/dev_ws/src && cd ~/dev_ws/src
git clone https://github.com/merpe24/my_bot.git
cd ~/dev_ws && colcon build --symlink-install && source install/setup.bash
```

Run the commands below from the workspace root, one per terminal.

```bash
# Simulation: Gazebo room world, robot, controllers
ros2 launch my_bot launch_sim.launch.py

# Drive it
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/diff_cont/cmd_vel -p stamped:=true

# Map the room, then save the result
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true \
  slam_params_file:=src/my_bot/config/mapper_params_online_async.yaml
ros2 run nav2_map_server map_saver_cli -f src/my_bot/maps/my_map
```

Autonomous navigation on the saved map needs three more terminals alongside the simulation: localization, the navigation stack, and the velocity mux. Set goals from RViz with *2D Goal Pose*.

```bash
ros2 launch nav2_bringup localization_launch.py use_sim_time:=true \
  map:=src/my_bot/maps/room_map.yaml params_file:=src/my_bot/config/nav2_params.yaml

ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true \
  params_file:=src/my_bot/config/nav2_params.yaml

ros2 run twist_mux twist_mux --ros-args --params-file src/my_bot/config/twist_mux.yaml \
  -r cmd_vel_out:=/diff_cont/cmd_vel -p use_sim_time:=true

rviz2 -d src/my_bot/config/drive_bot.rviz --ros-args -p use_sim_time:=true
```

On the real robot, `ros2 launch my_bot launch_robot.launch.py` starts the same controllers against the Arduino. It needs [diffdrive_arduino](https://github.com/joshnewans/diffdrive_arduino) (`humble` branch, which builds on Jazzy) and `libserial-dev` in the workspace.

## Layout

```
description/   URDF/xacro model, sensors, ros2_control (sim/hardware switch)
launch/        rsp, launch_sim, launch_robot
config/        controllers, SLAM, Nav2, twist_mux, gz bridge, RViz
worlds/        room, obstacles, empty
maps/          saved map of the test room (occupancy grid + pose graph)
```

## Notes

- Jazzy's `diff_drive_controller` expects `TwistStamped` on `/diff_cont/cmd_vel`, while Nav2 publishes `Twist` on `/cmd_vel`, and a remap cannot change a message type. Nav2's velocity publishers are configured with `enable_stamped_cmd_vel`, and `twist_mux` merges them with teleop into the controller's topic.
- `slam_toolbox` and AMCL are both pointed at `base_link`; this robot has no `base_footprint` frame.
- A Gazebo world must load `gz-sim-sensors-system` and the GPU lidar system, otherwise sensors advertise their topics but never publish.

## Credits

Started from the [Articulated Robotics](https://articulatedrobotics.xyz/) tutorial series and ported to Jazzy, Gazebo Harmonic and `ros_gz`. The hardware interface is [joshnewans/diffdrive_arduino](https://github.com/joshnewans/diffdrive_arduino). Apache License 2.0.
