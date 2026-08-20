cmake_minimum_required(VERSION 3.8)
project(practical_1_mobile_robot_urdf)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES my_robot.urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
