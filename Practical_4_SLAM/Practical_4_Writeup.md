# Practical 4: Implement SLAM Using ROS 2

## Objective
The objective of this practical is to create a map of an unknown environment while simultaneously determining the robot's location. We achieve this by using the Simultaneous Localization and Mapping (SLAM) algorithm.

## Software Required
1. **SLAM Toolbox**
   * **Purpose**: Provides highly optimized algorithms for Simultaneous Localization and Mapping (SLAM). It listens to LaserScan data and Odometry to build a 2D occupancy grid map.
2. **TurtleBot3**
   * **Purpose**: Provides a ready-made, reliable robot model equipped with LiDAR and odometry, which is perfect for SLAM experiments.

## 1. Installation

To install the required software packages for ROS 2 Humble, run the following commands in your terminal:

```bash
sudo apt update
sudo apt install ros-humble-slam-toolbox
sudo apt install ros-humble-turtlebot3*
```

## 2. Launching TurtleBot3 in Simulation

Before launching, we need to specify which TurtleBot3 model we want to use (e.g., `burger`, `waffle`, or `waffle_pi`). In this practical, we will use the `waffle` model.

1. Open a new terminal.
2. Set the model environment variable and launch the TurtleBot3 house simulation:

```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

Gazebo will open, showing the TurtleBot3 robot inside a complex house environment.

## 3. Running SLAM Toolbox

Now that the robot and environment are running, we will start the SLAM node to process the LiDAR data and begin building the map.

1. Open a **second** terminal.
2. Ensure the `use_sim_time` parameter is set to true so SLAM syncs with Gazebo's clock, and launch the online asynchronous mapping node:

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```
*(Optional)* You can also launch RViz to visualize the mapping process:
```bash
ros2 run rviz2 rviz2
```
*(In RViz, add the `Map` display and set the topic to `/map` to see the map being built in real-time).*

## 4. Moving the Robot (Teleoperation)

To map the unknown environment, the robot needs to explore it. We will use a teleoperation node to drive the robot around manually.

1. Open a **third** terminal.
2. Set the model environment variable and launch the teleoperation node:

```bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```
Use the `w`, `a`, `s`, `d`, and `x` keys to drive the robot through the house. As it moves, the SLAM Toolbox will expand the map.

## 5. Saving the Generated Map

Once you have explored the environment and are satisfied with the generated map in RViz, you must save it to a file. The map is saved as two files: a `.yaml` file containing the map metadata, and a `.pgm` image file containing the actual grid map.

1. Open a **fourth** terminal.
2. Run the `nav2_map_server` map saver node to save the map into your current directory:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_house_map
```

This command will output two files in your home directory: `my_house_map.yaml` and `my_house_map.pgm`.

## Conclusion
In this practical, we successfully implemented SLAM in ROS 2. We utilized the TurtleBot3 simulation package and SLAM Toolbox to explore an unknown Gazebo environment, visualized the real-time map generation, and saved the final occupancy grid map using the map saver CLI.
