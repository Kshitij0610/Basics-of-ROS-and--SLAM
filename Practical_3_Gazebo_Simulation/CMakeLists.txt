cmake_minimum_required(VERSION 3.8)
project(practical_3_gazebo_simulation)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf config scripts
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/arm_teleop.py
    scripts/base_teleop.py
    scripts/combined_teleop.py
    scripts/launch_sim.sh
    scripts/kill_sim.sh
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
