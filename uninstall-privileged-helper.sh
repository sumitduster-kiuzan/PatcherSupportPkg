#!/bin/bash

# OpenCore Legacy Patcher Privileged Helper Tool Uninstallation Script

set -e

HELPER_NAME="com.sumitduster.opencore-legacy-patcher.privileged-helper"
PLIST_NAME="${HELPER_NAME}.plist"
INSTALL_DIR="/Library/PrivilegedHelperTools"
LAUNCHD_DIR="/Library/LaunchDaemons"

echo "OpenCore Legacy Patcher Privileged Helper Tool Uninstaller"
echo "=========================================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Stop and unload the service
echo "Stopping privileged helper service..."
launchctl unload "$LAUNCHD_DIR/$PLIST_NAME" 2>/dev/null || true

# Remove files
echo "Removing privileged helper files..."
rm -f "$INSTALL_DIR/$HELPER_NAME"
rm -f "$LAUNCHD_DIR/$PLIST_NAME"

# Clean up log files
rm -f "/var/log/opencore-legacy-patcher-privileged-helper.log"

echo "✅ Privileged helper tool uninstalled successfully!"