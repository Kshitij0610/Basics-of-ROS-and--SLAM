#!/bin/bash
# =============================================================================
#  kill_slam.sh — Cleanly shut down the entire SLAM pipeline
# =============================================================================
#  Run this when you are done with the practical or if anything freezes.
#
#  USAGE:
#    ./kill_slam.sh
# =============================================================================

echo "🛑 Shutting down SLAM pipeline..."

# Kill the tmux session (closes all 4 windows at once)
tmux kill-session -t practical4_slam 2>/dev/null

# Force kill any remaining Gazebo processes
killall -9 gzserver gzclient 2>/dev/null

# Kill any lingering ROS nodes
pkill -f "slam_toolbox" 2>/dev/null
pkill -f "teleop_keyboard" 2>/dev/null
pkill -f "map_saver" 2>/dev/null
pkill -f "rviz2" 2>/dev/null

echo "✅ All SLAM processes killed. Environment is clean."
echo "   You can now safely run launch_slam.sh again."
