import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='my_bot' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Find the exact filepath to your custom world
    world_path = os.path.join(get_package_share_directory(package_name), 'worlds', 'obstacles.world')

    # Include the Gazebo launch file, explicitly passing in the world_path
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': ['-r ', world_path]}.items()
    )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-name', 'my_bot',
                                   '-z', '0.1'],
                        output='screen')

    # Bridge ROS topics and Gazebo messages for cmd_vel, odom, and TF
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/model/my_bot/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model'
        ],
        remappings=[
            ('/model/my_bot/tf', '/tf')
        ],
        output='screen'
    )



    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge,
    ])