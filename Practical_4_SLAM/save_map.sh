#!/bin/bash
# =============================================================================
#  save_map.sh — Save the SLAM-generated map to files
# =============================================================================
#  Run this AFTER you have driven the robot through the environment and
#  you are satisfied with the map visible in RViz.
#
#  USAGE:
#    ./save_map.sh                  → saves to ~/maps/my_house_map
#    ./save_map.sh my_custom_name   → saves to ~/maps/my_custom_name
#
#  OUTPUT FILES:
#    <map_name>.yaml   → map metadata (resolution, origin, image path)
#    <map_name>.pgm    → grayscale occupancy grid image
#                         white  = free space (robot can drive here)
#                         black  = wall / obstacle
#                         grey   = unknown (robot hasn't been there)
#
#  CUSTOMISABLE:
#    MAP_DIR → change the folder where maps are saved
# =============================================================================

# ── Configuration ─────────────────────────────────────────────────────────────

# ★ CHANGE THIS: Directory where maps will be saved
MAP_DIR="$HOME/maps"

# Map name — use first argument if given, otherwise use timestamp
if [ -n "$1" ]; then
    MAP_NAME="$1"
else
    MAP_NAME="house_map_$(date +%Y%m%d_%H%M%S)"
fi

# ── Create output directory ────────────────────────────────────────────────────
mkdir -p "$MAP_DIR"

# ── Source ROS ────────────────────────────────────────────────────────────────
source /opt/ros/humble/setup.bash

# ── Save the map ──────────────────────────────────────────────────────────────
echo ""
echo "💾 Saving map to: $MAP_DIR/$MAP_NAME"
echo "   (This may take a few seconds...)"
echo ""

ros2 run nav2_map_server map_saver_cli \
    --ros-args -p use_sim_time:=true \
    -- -f "$MAP_DIR/$MAP_NAME"

# ── Verify ────────────────────────────────────────────────────────────────────
if [ -f "$MAP_DIR/$MAP_NAME.yaml" ] && [ -f "$MAP_DIR/$MAP_NAME.pgm" ]; then
    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "✅ Map saved successfully!"
    echo "══════════════════════════════════════════════════════"
    echo "  YAML : $MAP_DIR/$MAP_NAME.yaml"
    echo "  Image: $MAP_DIR/$MAP_NAME.pgm"
    echo ""
    echo "  You can view the map image with:"
    echo "    eog $MAP_DIR/$MAP_NAME.pgm"
    echo "  Or open the .yaml in any text editor to see resolution/origin."
    echo "══════════════════════════════════════════════════════"
else
    echo ""
    echo "❌ Map save failed!"
    echo "   Make sure:"
    echo "   1. SLAM Toolbox is still running (Window 1 in tmux)"
    echo "   2. nav2_map_server is installed:"
    echo "      sudo apt install ros-humble-nav2-map-server"
    exit 1
fi
