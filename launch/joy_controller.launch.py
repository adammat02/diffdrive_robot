import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'diffdrive_robot'

    use_sim_time = LaunchConfiguration('use_sim_time')

    use_sim_time_args = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use sim time if true'
    )

    joy_config = os.path.join(
        get_package_share_directory(pkg_name), 'config', 'joy_config.yaml'
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[{'use_sim_time': use_sim_time}, joy_config]
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_node',
        parameters=[{'use_sim_time': use_sim_time}, joy_config]
    )

    return LaunchDescription([
        use_sim_time_args,
        joy_node,
        teleop_node
    ])
