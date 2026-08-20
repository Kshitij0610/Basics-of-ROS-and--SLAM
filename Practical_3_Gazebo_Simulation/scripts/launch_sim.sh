#!/bin/bash
# =============================================================================
#  launch_sim.sh — Portable One-click launcher for Practical 3 (Gazebo + Arm + Base)
# =============================================================================
#  Opens a tmux session with 3 windows so you don't have to manage terminals.
#
#  USAGE:
#    chmod +x launch_sim.sh    (first time only)
#    ./launch_sim.sh
#
#  WINDOWS:
#    0 — Gazebo  : physics simulation + robot spawn + controllers
#    1 — ArmTele : arm_teleop.py (keys 1–6 to move arm joints)
#    2 — BaseTele: base_teleop.py (w/a/s/d to drive wheels)
# =============================================================================

SESSION_NAME="practical3_sim"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Prevent Gazebo from hanging on online model downloads
export GAZEBO_MODEL_DATABASE_URI=""

# ── Check for existing session ─────────────────────────────────────────────────
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️  Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

echo "🚀 Launching Practical 3 — Gazebo Mobile Manipulator Simulation..."

# ── Window 0: Gazebo ──────────────────────────────────────────────────────────
tmux new-session -d -s "$SESSION_NAME" -n "Gazebo"
tmux send-keys -t "$SESSION_NAME:Gazebo" \
    "source /opt/ros/humble/setup.bash && \
     if [ -f \$HOME/ros2_ws/install/setup.bash ]; then source \$HOME/ros2_ws/install/setup.bash; fi && \
     echo '⏳ Launching Gazebo simulation...' && \
     ros2 launch practical_3_gazebo_simulation gazebo.launch.py 2>/dev/null || ros2 launch '$PKG_DIR/launch/gazebo.launch.py'" C-m

echo "✅ Window 1/3 — Gazebo launched. Waiting 15s for controllers to start..."
sleep 15

# ── Window 1: Arm Teleop ──────────────────────────────────────────────────────
tmux new-window -t "$SESSION_NAME" -n "ArmTele"
tmux send-keys -t "$SESSION_NAME:ArmTele" \
    "source /opt/ros/humble/setup.bash && \
     if [ -f \$HOME/ros2_ws/install/setup.bash ]; then source \$HOME/ros2_ws/install/setup.bash; fi && \
     echo '🦾 Arm Teleop Ready! Keys: 1/2=J1  3/4=J2  5/6=J3  q=quit' && \
     python3 '$SCRIPT_DIR/arm_teleop.py'" C-m

echo "✅ Window 2/3 — Arm teleop ready."
sleep 1

# ── Window 2: Base Teleop ─────────────────────────────────────────────────────
tmux new-window -t "$SESSION_NAME" -n "BaseTele"
tmux send-keys -t "$SESSION_NAME:BaseTele" \
    "source /opt/ros/humble/setup.bash && \
     echo '🚗 Base Teleop Ready! Keys: w/a/s/d=drive  x=stop  Ctrl+C=quit' && \
     python3 '$SCRIPT_DIR/base_teleop.py'" C-m

echo "✅ Window 3/3 — Base teleop ready."

# ── Select base teleop window (most used) ─────────────────────────────────────
tmux select-window -t "$SESSION_NAME:BaseTele"

echo ""
echo "══════════════════════════════════════════════════════════"
echo " Practical 3 is running in tmux session: $SESSION_NAME"
echo "══════════════════════════════════════════════════════════"
echo " Ctrl+B, then 0 → Gazebo window"
echo " Ctrl+B, then 1 → Arm Teleop  (keys 1–6)"
echo " Ctrl+B, then 2 → Base Teleop (w/a/s/d)"
echo " Ctrl+B, then d → detach (simulation keeps running)"
echo ""
echo " To stop everything: ./kill_sim.sh"
echo "══════════════════════════════════════════════════════════"

tmux attach-session -t "$SESSION_NAME"
