import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Arduino hardware interface
    Run this on the Pi, NOT in simulation. It uses the diffdrive_arduino
    ros2_control plugin selected by ros2_control.xacro when sim_mode:=false.
    """

    package_name = 'my_bot'

    # robot_state_publisher with the REAL hardware description (sim_mode:=false)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'false', 'sim_mode': 'false'}.items()
    )

    controller_params_file = os.path.join(
        get_package_share_directory(package_name), 'config', 'my_controllers.yaml')

    # Controller_manager auto-subscribes to /robot_description,
    # so we only need to give it the controllers config.
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[controller_params_file],
        output='screen',
    )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    # Wait until the controller_manager is up before spawning controllers.
    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])
    delayed_spawners = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner, joint_broad_spawner],
        )
    )

    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_spawners,
    ])
