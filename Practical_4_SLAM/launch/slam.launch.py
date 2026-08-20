import os
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'practical_4_slam'
    
    # ── Portable Package Share Resolution ─────────────────────────────────────
    try:
        pkg_path = get_package_share_directory(pkg_name)
    except PackageNotFoundError:
        pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
    slam_params_file = os.path.join(pkg_path, 'slam_params.yaml')
    rviz_config_file = os.path.join(pkg_path, 'slam_rviz.rviz')
    
    # 1. Gazebo TurtleBot3 House World
    tb3_gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch', 'turtlebot3_house.launch.py')
        )
    )

    # 2. SLAM Toolbox Online Async Mapping
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_params_file
        }.items()
    )

    # 3. RViz2 Visualization Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        tb3_gazebo_launch,
        slam_toolbox_launch,
        rviz_node
    ])
