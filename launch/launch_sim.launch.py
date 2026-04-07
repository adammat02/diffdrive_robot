import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    
    package_name = "diffdrive_robot"

    use_ros2_control = LaunchConfiguration('use_ros2_control')

    use_ros2_control_args = DeclareLaunchArgument(
        'use_ros2_control',
        default_value='true',
        description='Use ros2_control if true'
    )

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
            )]),
            launch_arguments={'use_sim_time': 'true', 'use_ros2_control': use_ros2_control}.items()
    )

    world = LaunchConfiguration('world')

    world_args = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='World to load'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': ['-r -v4 ', world], 'on_exit_shutdown': 'true'}.items()
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'diffdrive_robot',
                   '-z', '0.1'],
        output='screen'
    )

    bridge_parameters = os.path.join(get_package_share_directory(package_name), 'config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_parameters}'
        ]
    )

    ros_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw']
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_cont',
            '--controller-ros-args',
            '-r /diff_cont/cmd_vel:=/cmd_vel'
        ]
    )

    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad']   
    )

    ekf_config = os.path.join(
        get_package_share_directory(package_name), 'config', 'ekf.yaml'
    )

    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': True}]
    )

    rviz_config = os.path.join(
        get_package_share_directory(package_name), 'config', 'rviz.rviz'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=[
            '-d',
            rviz_config
        ],
        output='screen'
    )

    return LaunchDescription([
        use_ros2_control_args,
        rsp,
        world_args,
        gazebo,
        spawn,
        ros_gz_bridge,
        ros_gz_image_bridge,
        diff_drive_spawner,
        joint_broad_spawner,
        ekf,
        rviz
    ])