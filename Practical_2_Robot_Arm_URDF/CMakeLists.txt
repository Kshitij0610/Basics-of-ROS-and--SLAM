cmake_minimum_required(VERSION 3.8)
project(practical_2_robot_arm_urdf)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf rviz config scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
