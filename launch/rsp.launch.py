import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Launch args
    use_sim_time = LaunchConfiguration('use_sim_time')
    sim_mode = LaunchConfiguration('sim_mode')

    # Process the URDF file, passing sim_mode through to ros2_control.xacro.
    # Using Command(['xacro ...]) defers evaluation to launch time so the
    # LaunchConfiguration substitutions actually get filled in.
    pkg_path = os.path.join(get_package_share_directory('my_bot'))
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    robot_description_config = ParameterValue(
        Command(['xacro ', xacro_file, ' sim_mode:=', sim_mode]),
        value_type=str)

    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config, 'use_sim_time': use_sim_time}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),
        DeclareLaunchArgument(
            'sim_mode',
            default_value='false',
            description='Use gz_ros2_control (true) or the Arduino hardware interface (false)'),

        node_robot_state_publisher
    ])
