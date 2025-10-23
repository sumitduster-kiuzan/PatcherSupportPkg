#!/bin/bash

# OpenCore Legacy Patcher Privileged Helper Tool Installation Script

set -e

HELPER_NAME="com.sumitduster.opencore-legacy-patcher.privileged-helper"
PLIST_NAME="${HELPER_NAME}.plist"
INSTALL_DIR="/Library/PrivilegedHelperTools"
LAUNCHD_DIR="/Library/LaunchDaemons"

echo "OpenCore Legacy Patcher Privileged Helper Tool Installer"
echo "======================================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Build the helper tool if it doesn't exist
if [[ ! -f "$HELPER_NAME" ]]; then
    echo "Building privileged helper tool..."
    make build
fi

# Create directories if they don't exist
mkdir -p "$INSTALL_DIR"
mkdir -p "$LAUNCHD_DIR"

# Stop existing service if running
echo "Stopping existing service (if any)..."
launchctl unload "$LAUNCHD_DIR/$PLIST_NAME" 2>/dev/null || true

# Install the helper tool
echo "Installing privileged helper tool..."
cp "$HELPER_NAME" "$INSTALL_DIR/"
cp "$PLIST_NAME" "$LAUNCHD_DIR/"

# Set proper permissions
chown root:wheel "$INSTALL_DIR/$HELPER_NAME"
chown root:wheel "$LAUNCHD_DIR/$PLIST_NAME"
chmod 755 "$INSTALL_DIR/$HELPER_NAME"
chmod 644 "$LAUNCHD_DIR/$PLIST_NAME"

# Load the service
echo "Loading privileged helper service..."
launchctl load "$LAUNCHD_DIR/$PLIST_NAME"

# Verify installation
if launchctl list | grep -q "$HELPER_NAME"; then
    echo "✅ Privileged helper tool installed and loaded successfully!"
else
    echo "❌ Failed to load privileged helper tool"
    exit 1
fi

echo ""
echo "Installation complete!"
echo "The privileged helper tool is now available at: $INSTALL_DIR/$HELPER_NAME"
echo ""
echo "To uninstall, run: sudo ./uninstall-privileged-helper.sh"