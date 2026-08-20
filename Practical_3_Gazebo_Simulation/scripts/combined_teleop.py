#!/usr/bin/env python3
"""
combined_teleop.py — Control BOTH the base AND the arm from a single terminal (Practical 3)
============================================================================================
This script runs two independent ROS 2 publishers in one terminal:
  1. Base driver  → publishes Twist to /cmd_vel  (drives the wheels)
  2. Arm driver   → publishes JointTrajectory to /arm_controller/joint_trajectory

Press TAB to toggle which subsystem your keys are controlling.

CONTROLS:
    ── Base Mode (default) ──────────────────────
    w / s        → forward / backward
    a / d        → turn left / right
    x            → STOP base
    + / -        → change base speed

    ── Arm Mode (press TAB to switch) ──────────
    1 / 2        → Joint 1 (Yaw)   − / +
    3 / 4        → Joint 2 (Pitch) − / +
    5 / 6        → Joint 3 (Pitch) − / +
    0            → Reset arm to home (all zeros)
    + / -        → change arm step size

    ── Always available ─────────────────────────
    TAB          → toggle between Base and Arm mode
    Ctrl+C       → quit (stops base and holds arm position)

CUSTOMISABLE VALUES:
    BASE_SPEED      → default linear speed of base (m/s)
    BASE_TURN       → default angular speed of base (rad/s)
    ARM_STEP        → radians per keypress for each arm joint
    ARM_MOVE_TIME   → seconds for arm to reach each commanded position
"""

import sys
import termios
import tty
import select
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# ══════════════════════════════════════════════════════════════════
#  ★ CUSTOMISABLE — edit these values
# ══════════════════════════════════════════════════════════════════

BASE_SPEED    = 0.20   # m/s    — default forward speed of mobile base
BASE_TURN     = 0.60   # rad/s  — default rotation speed of mobile base
ARM_STEP      = 0.10   # rad    — how much each 1/2/3 keypress moves a joint
                       #          decrease to 0.05 for finer control
ARM_MOVE_TIME = 0.5    # sec    — time for arm to reach the commanded position
                       #          decrease to 0.2 for snappier motion

# ══════════════════════════════════════════════════════════════════

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║         Combined Teleop: Base + Arm  (Practical 3)           ║
╠══════════════════════╦════════════════════════════════════════╣
║  BASE MODE           ║  ARM MODE  (press TAB to switch)      ║
║  w / s → fwd / back  ║  1/2 → Joint 1 (Yaw) −/+             ║
║  a / d → left / right║  3/4 → Joint 2 (Pitch1) −/+          ║
║  x     → STOP        ║  5/6 → Joint 3 (Pitch2) −/+          ║
║  + / - → speed       ║  0   → Reset arm to home              ║
║                      ║  + / - → step size                    ║
╠══════════════════════╩════════════════════════════════════════╣
║  TAB → toggle mode   |   Ctrl+C → quit                       ║
╚═══════════════════════════════════════════════════════════════╝
"""

BASE_KEYS = {
    'w': ( 1,  0),
    's': (-1,  0),
    'a': ( 0,  1),
    'd': ( 0, -1),
    'q': ( 1,  1),
    'e': ( 1, -1),
    'x': ( 0,  0),
}


class CombinedTeleop(Node):
    def __init__(self):
        super().__init__('combined_teleop')

        # Publishers
        self.base_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.arm_pub  = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)

        self.settings = termios.tcgetattr(sys.stdin)

        # Base state
        self.base_speed = BASE_SPEED
        self.base_turn  = BASE_TURN

        # Arm state — [joint_1, joint_2, joint_3] positions in radians
        self.arm_pos  = [0.0, 0.0, 0.0]
        self.arm_step = ARM_STEP

        # Mode: 'base' or 'arm'
        self.mode = 'base'

    # ── Key reading ───────────────────────────────────────────────────────────
    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    # ── Publishers ────────────────────────────────────────────────────────────
    def send_base(self, linear: float, angular: float):
        msg = Twist()
        msg.linear.x  = linear
        msg.angular.z = angular
        self.base_pub.publish(msg)

    def send_arm(self):
        msg = JointTrajectory()
        msg.joint_names = ['joint_1', 'joint_2', 'joint_3']
        pt = JointTrajectoryPoint()
        pt.positions = list(self.arm_pos)
        sec = int(ARM_MOVE_TIME)
        nsec = int((ARM_MOVE_TIME - sec) * 1e9)
        pt.time_from_start = Duration(sec=sec, nanosec=nsec)
        msg.points = [pt]
        self.arm_pub.publish(msg)

    # ── Status line ───────────────────────────────────────────────────────────
    def status(self, action=''):
        mode_str = '🚗 BASE ' if self.mode == 'base' else '🦾 ARM  '
        arm_str  = f'J1={self.arm_pos[0]:+.2f} J2={self.arm_pos[1]:+.2f} J3={self.arm_pos[2]:+.2f}'
        print(f'\r  [{mode_str}]  {arm_str}  | {action}   ', end='', flush=True)

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        print(BANNER)
        print(f'  Base speed: {self.base_speed:.2f} m/s  |  Arm step: {self.arm_step:.2f} rad')
        print()
        try:
            while rclpy.ok():
                key = self.get_key()

                # ── TAB: toggle mode ─────────────────────────────────────────
                if key == '\t':
                    self.mode = 'arm' if self.mode == 'base' else 'base'
                    self.send_base(0.0, 0.0)   # always stop base when switching
                    self.status('MODE SWITCHED')
                    continue

                # ── Quit ─────────────────────────────────────────────────────
                if key == '\x03':
                    break

                # ── BASE mode ─────────────────────────────────────────────────
                if self.mode == 'base':
                    if key in BASE_KEYS:
                        l, a = BASE_KEYS[key]
                        self.send_base(l * self.base_speed, a * self.base_turn)
                        lbl = 'STOP' if key == 'x' else f'lin={l*self.base_speed:+.2f}'
                        self.status(lbl)
                    elif key == '+':
                        self.base_speed = min(self.base_speed + 0.05, 1.0)
                        self.status(f'speed={self.base_speed:.2f}')
                    elif key == '-':
                        self.base_speed = max(self.base_speed - 0.05, 0.05)
                        self.status(f'speed={self.base_speed:.2f}')

                # ── ARM mode ──────────────────────────────────────────────────
                elif self.mode == 'arm':
                    moved = True
                    if key == '1':
                        self.arm_pos[0] = max(self.arm_pos[0] - self.arm_step, -3.14159)
                    elif key == '2':
                        self.arm_pos[0] = min(self.arm_pos[0] + self.arm_step,  3.14159)
                    elif key == '3':
                        self.arm_pos[1] = max(self.arm_pos[1] - self.arm_step, -1.5708)
                    elif key == '4':
                        self.arm_pos[1] = min(self.arm_pos[1] + self.arm_step,  1.5708)
                    elif key == '5':
                        self.arm_pos[2] = max(self.arm_pos[2] - self.arm_step, -1.5708)
                    elif key == '6':
                        self.arm_pos[2] = min(self.arm_pos[2] + self.arm_step,  1.5708)
                    elif key == '0':
                        self.arm_pos = [0.0, 0.0, 0.0]   # reset to home
                    elif key == '+':
                        self.arm_step = min(self.arm_step + 0.01, 0.5)
                        moved = False
                        self.status(f'step={self.arm_step:.2f}')
                    elif key == '-':
                        self.arm_step = max(self.arm_step - 0.01, 0.01)
                        moved = False
                        self.status(f'step={self.arm_step:.2f}')
                    else:
                        moved = False

                    if moved:
                        self.send_arm()
                        self.status()

        except Exception as e:
            print(f'\nError: {e}')
        finally:
            self.send_base(0.0, 0.0)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            print('\n\n  Combined teleop stopped. Base halted.')


def main(args=None):
    rclpy.init(args=args)
    node = CombinedTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
