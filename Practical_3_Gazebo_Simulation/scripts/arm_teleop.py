#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys
import termios
import tty
import select

msg = """
Reading from the keyboard and Publishing to JointTrajectory!
---------------------------
Controls:
   1 / 2 : Decrease / Increase Joint 1 (Yaw)
   3 / 4 : Decrease / Increase Joint 2 (Pitch 1)
   5 / 6 : Decrease / Increase Joint 3 (Pitch 2)

q : quit
"""

class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')
        self.publisher_ = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.joint_positions = [0.0, 0.0, 0.0]
        self.step_size = 0.1

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_trajectory(self):
        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['joint_1', 'joint_2', 'joint_3']
        point = JointTrajectoryPoint()
        point.positions = self.joint_positions
        point.time_from_start = Duration(sec=0, nanosec=500000000) # 0.5 sec to reach target
        traj_msg.points = [point]
        self.publisher_.publish(traj_msg)

    def run(self):
        print(msg)
        try:
            while rclpy.ok():
                key = self.get_key()
                if key == 'q':
                    break
                elif key == '1':
                    self.joint_positions[0] -= self.step_size
                    self.publish_trajectory()
                elif key == '2':
                    self.joint_positions[0] += self.step_size
                    self.publish_trajectory()
                elif key == '3':
                    self.joint_positions[1] -= self.step_size
                    self.publish_trajectory()
                elif key == '4':
                    self.joint_positions[1] += self.step_size
                    self.publish_trajectory()
                elif key == '5':
                    self.joint_positions[2] -= self.step_size
                    self.publish_trajectory()
                elif key == '6':
                    self.joint_positions[2] += self.step_size
                    self.publish_trajectory()
                
        except Exception as e:
            print(e)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main(args=None):
    rclpy.init(args=args)
    node = ArmTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
