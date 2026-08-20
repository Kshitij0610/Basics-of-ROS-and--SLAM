#!/bin/bash
# =============================================================================
#  kill_sim.sh — Cleanly shut down the Practical 3 simulation
# =============================================================================
#  USAGE:
#    ./kill_sim.sh
# =============================================================================

echo "🛑 Shutting down Practical 3 simulation..."

tmux kill-session -t practical3_sim 2>/dev/null
killall -9 gzserver gzclient 2>/dev/null
pkill -f "arm_teleop"    2>/dev/null
pkill -f "base_teleop"   2>/dev/null
pkill -f "combined_teleop" 2>/dev/null
pkill -f "gazebo.launch" 2>/dev/null

echo "✅ All processes killed. Environment is clean."
echo "   Run ./launch_sim.sh to start again."
