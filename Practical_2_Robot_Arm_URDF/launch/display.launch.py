import os
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import xacro

def generate_launch_description():
    pkg_name = 'practical_2_robot_arm_urdf'
    
    # ── Portable Package Share Resolution ─────────────────────────────────────
    # Tries finding installed package via colcon build share directory.
    # Fallback to current directory path so launch works directly without colcon build!
    try:
        pkg_path = get_package_share_directory(pkg_name)
    except PackageNotFoundError:
        pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # ── Locate Xacro and RViz files ──────────────────────────────────────────
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot_arm_standalone.xacro')
    if not os.path.exists(xacro_file):
        xacro_file = os.path.join(pkg_path, 'urdf', 'robot_arm.urdf.xacro')
        
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    rviz_config_file = os.path.join(pkg_path, 'rviz', 'display.rviz')
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # ── Nodes ─────────────────────────────────────────────────────────────────
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )
    
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        parameters=[robot_description]
    )
    
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'),
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node
    ])
