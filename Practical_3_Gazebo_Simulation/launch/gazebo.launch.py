import os
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'practical_3_gazebo_simulation'
    
    # ── Portable Package Share Resolution ─────────────────────────────────────
    # Tries finding installed package via colcon build share directory.
    # Fallback to local path so launch works directly without colcon build!
    try:
        pkg_path = get_package_share_directory(pkg_name)
    except PackageNotFoundError:
        pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot_arm.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        )
    )
    
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'mobile_manipulator', '-topic', 'robot_description'],
        output='screen'
    )
    
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        spawn_entity,
        joint_state_broadcaster_spawner,
        arm_controller_spawner
    ])
