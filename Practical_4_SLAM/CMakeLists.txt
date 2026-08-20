cmake_minimum_required(VERSION 3.8)
project(practical_4_slam)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES
    slam_params.yaml
    slam_rviz.rviz
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    teleop_base.py
    launch_slam.sh
    save_map.sh
    kill_slam.sh
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
