#!/bin/bash
#
# WebDoom - Pygame Edition
# Start script
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Add src to PYTHONPATH so we get local config, not site-packages
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Check for display availability
if [ -z "$DISPLAY" ] && [ "$SDL_VIDEODRIVER" != "dummy" ]; then
    echo "No display detected. Running in headless mode..."
    export SDL_VIDEODRIVER=dummy
    export SDL_AUDIODRIVER=dummy
fi

# Run the game using uv
echo "Starting WebDoom..."
uv run python -m src.game "$@"