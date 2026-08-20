#!/usr/bin/env python3
"""
base_teleop.py — Keyboard teleoperation for the Mobile Robot Base (Practical 3)
================================================================================
Drives the 4-wheel skid-steer base by publishing Twist messages to /cmd_vel,
which is consumed by the libgazebo_ros_diff_drive Gazebo plugin in mobile_base.xacro.

USAGE:
    # Make executable (first time only):
    chmod +x base_teleop.py

    # Run directly:
    python3 base_teleop.py

CONTROLS:
    w / s   → forward / backward
    a / d   → turn left / right
    q / e   → diagonal (forward-left / forward-right)
    x       → STOP immediately
    + / -   → increase / decrease linear speed
    ] / [   → increase / decrease turn speed
    Ctrl+C  → quit

CUSTOMISABLE VALUES:
    ┌─────────────────────┬────────────────────────────────────────────┐
    │ Variable            │ Effect                                     │
    ├─────────────────────┼────────────────────────────────────────────┤
    │ SPEED      (m/s)    │ Default forward speed. Max safe ≈ 0.5 m/s  │
    │ TURN_SPEED (rad/s)  │ Default rotation speed. Max safe ≈ 1.0     │
    │ STEP       (m/s)    │ Speed increment per +/- keypress           │
    └─────────────────────┴────────────────────────────────────────────┘
"""

import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# ══════════════════════════════════════════════════════════════════
#  ★ CUSTOMISABLE — change these to alter robot speed
# ══════════════════════════════════════════════════════════════════

SPEED       = 0.20   # m/s   — try 0.10 for cautious, 0.40 for fast
TURN_SPEED  = 0.60   # rad/s — try 0.30 for gentle turns
STEP        = 0.05   # m/s   — speed change per +/- keypress

# ══════════════════════════════════════════════════════════════════

MSG = """
╔════════════════════════════════════════════════╗
║  Mobile Base Keyboard Teleop  (Practical 3)    ║
╠════════════════════════════════════════════════╣
║   w / s     → forward / backward               ║
║   a / d     → turn left / right                ║
║   q / e     → diagonal forward (L / R)         ║
║   x         → STOP immediately                 ║
║   + / -     → increase / decrease speed        ║
║   ] / [     → increase / decrease turn speed   ║
║   Ctrl+C    → quit                             ║
╚════════════════════════════════════════════════╝
"""

KEY_MAP = {
    'w': ( 1,  0),
    's': (-1,  0),
    'a': ( 0,  1),
    'd': ( 0, -1),
    'q': ( 1,  1),
    'e': ( 1, -1),
    'x': ( 0,  0),
}


class BaseTeleop(Node):
    def __init__(self):
        super().__init__('base_teleop')
        # /cmd_vel is the topic the skid-steer Gazebo plugin listens to
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.speed      = SPEED
        self.turn_speed = TURN_SPEED

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish(self, linear: float, angular: float):
        msg = Twist()
        msg.linear.x  = linear
        msg.angular.z = angular
        self.pub.publish(msg)

    def run(self):
        print(MSG)
        print(f'  Speed: {self.speed:.2f} m/s  |  Turn: {self.turn_speed:.2f} rad/s')
        try:
            while rclpy.ok():
                key = self.get_key()
                if key in KEY_MAP:
                    l, a = KEY_MAP[key]
                    self.publish(l * self.speed, a * self.turn_speed)
                    status = 'STOP' if key == 'x' else f'lin={l*self.speed:+.2f} ang={a*self.turn_speed:+.2f}'
                    print(f'\r  ▶  {status}   ', end='', flush=True)
                elif key == '+':
                    self.speed = min(self.speed + STEP, 1.0)
                    print(f'\r  Speed ↑ {self.speed:.2f} m/s   ', end='', flush=True)
                elif key == '-':
                    self.speed = max(self.speed - STEP, 0.05)
                    print(f'\r  Speed ↓ {self.speed:.2f} m/s   ', end='', flush=True)
                elif key == ']':
                    self.turn_speed = min(self.turn_speed + STEP, 2.0)
                    print(f'\r  Turn ↑ {self.turn_speed:.2f} rad/s   ', end='', flush=True)
                elif key == '[':
                    self.turn_speed = max(self.turn_speed - STEP, 0.1)
                    print(f'\r  Turn ↓ {self.turn_speed:.2f} rad/s   ', end='', flush=True)
                elif key == '\x03':
                    break
        except Exception as e:
            print(f'\nError: {e}')
        finally:
            self.publish(0.0, 0.0)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            print('\n\n  Base teleop stopped. Robot halted.')


def main(args=None):
    rclpy.init(args=args)
    node = BaseTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
