#!/bin/bash
# =============================================================================
#  launch_slam.sh — One-click SLAM launcher for Practical 4
# =============================================================================
#  This script opens a tmux session with 4 windows, each running one part
#  of the SLAM pipeline so you don't have to open 4 terminals manually.
#
#  USAGE:
#    chmod +x launch_slam.sh    (first time only)
#    ./launch_slam.sh
#
#  CUSTOMISABLE:
#    ROBOT_MODEL  → change to "burger" or "waffle_pi" for a different robot
#    WORLD        → change the Gazebo world (see WORLDS section below)
#    USE_CUSTOM_PARAMS → set to "true" to use slam_params.yaml in this folder
# =============================================================================

# ── Configuration ─────────────────────────────────────────────────────────────

# ★ CHANGE THIS: Robot model — burger | waffle | waffle_pi
ROBOT_MODEL="waffle"

# ★ CHANGE THIS: Gazebo world to load
# Options:
#   turtlebot3_house    → complex house (best for mapping practice)
#   turtlebot3_world    → simple obstacle course
#   turtlebot3_dqn_stage1 → narrow corridor
WORLD="turtlebot3_house"

# ★ CHANGE THIS: Use custom slam_params.yaml from this folder (true/false)
USE_CUSTOM_PARAMS="true"

# Path to this script's directory (where slam_params.yaml lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# tmux session name
SESSION="practical4_slam"

# ── Prevent Gazebo download freeze ────────────────────────────────────────────
export GAZEBO_MODEL_DATABASE_URI=""

# ── Check for existing session ─────────────────────────────────────────────────
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "⚠️  Session '$SESSION' already exists. Attaching..."
    tmux attach-session -t "$SESSION"
    exit 0
fi

echo "🚀 Starting SLAM Pipeline for Practical 4..."
echo "   Robot Model : $ROBOT_MODEL"
echo "   World       : $WORLD"
echo "   Custom Params: $USE_CUSTOM_PARAMS"
echo ""

# ── Create tmux session ────────────────────────────────────────────────────────

# Window 0: Gazebo + TurtleBot3
tmux new-session -d -s "$SESSION" -n "Gazebo"
tmux send-keys -t "$SESSION:Gazebo" \
    "export TURTLEBOT3_MODEL=$ROBOT_MODEL && \
     export GAZEBO_MODEL_DATABASE_URI='' && \
     source /opt/ros/humble/setup.bash && \
     echo '⏳ Launching TurtleBot3 in Gazebo...' && \
     ros2 launch turtlebot3_gazebo ${WORLD}.launch.py" C-m

echo "✅ Window 1/4 — Gazebo launched. Waiting 10s for it to load..."
sleep 10

# Window 1: SLAM Toolbox
tmux new-window -t "$SESSION" -n "SLAM"
if [ "$USE_CUSTOM_PARAMS" = "true" ]; then
    tmux send-keys -t "$SESSION:SLAM" \
        "source /opt/ros/humble/setup.bash && \
         echo '🗺️  Starting SLAM Toolbox (custom params)...' && \
         ros2 launch slam_toolbox online_async_launch.py \
             use_sim_time:=true \
             slam_params_file:=$SCRIPT_DIR/slam_params.yaml" C-m
else
    tmux send-keys -t "$SESSION:SLAM" \
        "source /opt/ros/humble/setup.bash && \
         echo '🗺️  Starting SLAM Toolbox (default params)...' && \
         ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true" C-m
fi

echo "✅ Window 2/4 — SLAM Toolbox started."
sleep 3

# Window 2: RViz2
tmux new-window -t "$SESSION" -n "RViz"
RVIZ_CONFIG="$SCRIPT_DIR/slam_rviz.rviz"
if [ -f "$RVIZ_CONFIG" ]; then
    tmux send-keys -t "$SESSION:RViz" \
        "source /opt/ros/humble/setup.bash && \
         echo '👁️  Opening RViz with SLAM config...' && \
         ros2 run rviz2 rviz2 -d $RVIZ_CONFIG" C-m
else
    tmux send-keys -t "$SESSION:RViz" \
        "source /opt/ros/humble/setup.bash && \
         echo '👁️  Opening RViz (no config — add Map display manually)...' && \
         ros2 run rviz2 rviz2" C-m
fi

echo "✅ Window 3/4 — RViz started."
sleep 2

# Window 3: Teleoperation
tmux new-window -t "$SESSION" -n "Teleop"
tmux send-keys -t "$SESSION:Teleop" \
    "export TURTLEBOT3_MODEL=$ROBOT_MODEL && \
     source /opt/ros/humble/setup.bash && \
     echo '🕹️  Keyboard Teleoperation Ready!' && \
     echo '   w/a/s/d = move, x = stop, q/z = speed up/down' && \
     ros2 run turtlebot3_teleop teleop_keyboard" C-m

echo "✅ Window 4/4 — Teleoperation ready."

# ── Switch to Teleop window (where user drives) ────────────────────────────────
tmux select-window -t "$SESSION:Teleop"

echo ""
echo "══════════════════════════════════════════════════════"
echo " All 4 components are running in tmux session: $SESSION"
echo "══════════════════════════════════════════════════════"
echo " Ctrl+B, then 0/1/2/3 → switch between windows"
echo " Ctrl+B, then d       → detach (everything keeps running)"
echo " To save the map, open a NEW terminal and run:"
echo "   ./save_map.sh"
echo " To shut everything down:"
echo "   ./kill_slam.sh"
echo "══════════════════════════════════════════════════════"

tmux attach-session -t "$SESSION"
