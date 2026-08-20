#!/usr/bin/env python3
"""
teleop_base.py — Keyboard teleoperation for TurtleBot3 base (Practical 4)
=========================================================================
A self-contained keyboard driver that publishes velocity commands to the
/cmd_vel topic so you can drive the TurtleBot3 around to build the SLAM map.

This gives you more control over speed than the default turtlebot3_teleop
package — you can edit SPEED and TURN_SPEED below.

USAGE:
    # Make executable (first time only):
    chmod +x teleop_base.py

    # Run:
    python3 teleop_base.py

    # Or after sourcing ROS:
    ros2 run --prefix 'python3' teleop_base teleop_base

CONTROLS:
    w / s   → drive forward / backward
    a / d   → turn left / right
    q / e   → diagonal forward-left / forward-right
    x       → stop immediately
    +  / -  → increase / decrease linear speed
    ] / [   → increase / decrease turn speed
    Ctrl+C  → quit

CUSTOMISABLE VALUES:
    SPEED      → default forward/backward speed (m/s)
    TURN_SPEED → default rotation speed (rad/s)
    STEP       → how much speed changes per +/- keypress
"""

import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# ══════════════════════════════════════════════════════════════════════════════
#  ★ CUSTOMISABLE PARAMETERS — edit these to change robot speed
# ══════════════════════════════════════════════════════════════════════════════

SPEED       = 0.15   # m/s  — default forward/backward speed
                     #        TurtleBot3 max: ~0.22 m/s (burger), ~0.26 m/s (waffle)
                     #        Slow (0.05) for accurate SLAM, fast (0.20) for quick exploration

TURN_SPEED  = 0.5    # rad/s — default turning speed
                     #        Slow (0.3) for gentle turns, fast (1.0) for sharp turns

STEP        = 0.01   # m/s  — how much each +/- keypress changes the speed

# ══════════════════════════════════════════════════════════════════════════════

MSG = """
╔══════════════════════════════════════════════╗
║   TurtleBot3 SLAM Teleoperation (Practical 4)║
╠══════════════════════════════════════════════╣
║   w / s     → forward / backward             ║
║   a / d     → turn left / right              ║
║   q / e     → diagonal forward (L/R)         ║
║   x         → STOP immediately               ║
║   + / -     → increase / decrease speed      ║
║   ] / [     → increase / decrease turn speed ║
║   Ctrl+C    → quit                           ║
╚══════════════════════════════════════════════╝
"""

KEY_BINDINGS = {
    'w': ( 1,  0),   # forward
    's': (-1,  0),   # backward
    'a': ( 0,  1),   # turn left
    'd': ( 0, -1),   # turn right
    'q': ( 1,  1),   # forward + left
    'e': ( 1, -1),   # forward + right
    'x': ( 0,  0),   # stop
}


class TeleopBase(Node):
    def __init__(self):
        super().__init__('teleop_base')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.speed      = SPEED
        self.turn_speed = TURN_SPEED
        self.get_logger().info('Teleop node started. Drive the robot to build the SLAM map!')

    def get_key(self):
        """Read a single keypress without requiring Enter."""
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
        print(f'  Current speed : {self.speed:.3f} m/s')
        print(f'  Current turn  : {self.turn_speed:.3f} rad/s')
        print()
        try:
            while rclpy.ok():
                key = self.get_key()

                if key in KEY_BINDINGS:
                    lin_dir, ang_dir = KEY_BINDINGS[key]
                    self.publish(lin_dir * self.speed, ang_dir * self.turn_speed)
                    if key == 'x':
                        print('\r  ⏹  STOPPED', end='', flush=True)
                    else:
                        print(f'\r  ▶  lin={lin_dir * self.speed:+.3f}  ang={ang_dir * self.turn_speed:+.3f}   ', end='', flush=True)

                elif key == '+':
                    self.speed = min(self.speed + STEP, 0.26)
                    print(f'\r  Speed ↑ {self.speed:.3f} m/s   ', end='', flush=True)

                elif key == '-':
                    self.speed = max(self.speed - STEP, 0.01)
                    print(f'\r  Speed ↓ {self.speed:.3f} m/s   ', end='', flush=True)

                elif key == ']':
                    self.turn_speed = min(self.turn_speed + STEP * 5, 1.5)
                    print(f'\r  Turn ↑ {self.turn_speed:.3f} rad/s   ', end='', flush=True)

                elif key == '[':
                    self.turn_speed = max(self.turn_speed - STEP * 5, 0.1)
                    print(f'\r  Turn ↓ {self.turn_speed:.3f} rad/s   ', end='', flush=True)

                elif key == '\x03':   # Ctrl+C
                    break

        except Exception as e:
            print(f'\nError: {e}')
        finally:
            # Send stop command on exit
            self.publish(0.0, 0.0)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            print('\n\n  Teleop stopped. Robot halted.')


def main(args=None):
    rclpy.init(args=args)
    node = TeleopBase()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
