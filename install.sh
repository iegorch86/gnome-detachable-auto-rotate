#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

SOURCE_SCRIPT="$SCRIPT_DIR/dell-auto-rotate.py"
SOURCE_SERVICE="$SCRIPT_DIR/dell-auto-rotate.service"

TARGET_BIN="$HOME/.local/bin"
TARGET_SERVICE="$HOME/.config/systemd/user"

echo "Installing Dell 7210 auto rotation..."

if [[ ! -f "$SOURCE_SCRIPT" ]]; then
    echo "Error: dell-auto-rotate.py was not found."
    exit 1
fi

if [[ ! -f "$SOURCE_SERVICE" ]]; then
    echo "Error: dell-auto-rotate.service was not found."
    exit 1
fi

if ! command -v gdctl >/dev/null 2>&1; then
    echo "Error: gdctl is not installed or not available in PATH."
    exit 1
fi

if ! command -v monitor-sensor >/dev/null 2>&1; then
    echo "Error: monitor-sensor is not installed or not available in PATH."
    exit 1
fi

mkdir -p "$TARGET_BIN"
mkdir -p "$TARGET_SERVICE"

install -m 755 \
    "$SOURCE_SCRIPT" \
    "$TARGET_BIN/dell-auto-rotate.py"

install -m 644 \
    "$SOURCE_SERVICE" \
    "$TARGET_SERVICE/dell-auto-rotate.service"

systemctl --user daemon-reload
systemctl --user enable --now dell-auto-rotate.service

echo
echo "Installation completed."
echo
echo "Service status:"
systemctl --user --no-pager status dell-auto-rotate.service || true
echo
echo "Live logs:"
echo "journalctl --user -u dell-auto-rotate.service -f"
