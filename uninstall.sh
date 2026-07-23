#!/usr/bin/env bash

set -e

SCRIPT_PATH="$HOME/.local/bin/dell-auto-rotate.py"
SERVICE_PATH="$HOME/.config/systemd/user/dell-auto-rotate.service"

echo "Removing Dell 7210 auto rotation..."

systemctl --user disable --now dell-auto-rotate.service 2>/dev/null || true

rm -f "$SCRIPT_PATH"
rm -f "$SERVICE_PATH"

systemctl --user daemon-reload
systemctl --user reset-failed

echo "Uninstall completed."
