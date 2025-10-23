#!/bin/bash

# Mount helper script to handle sudo password issues
# Usage: ./mount_helper.sh <device> <mountpoint>

set -e

DEVICE="$1"
MOUNTPOINT="$2"

if [ -z "$DEVICE" ] || [ -z "$MOUNTPOINT" ]; then
    echo "Usage: $0 <device> <mountpoint>"
    echo "Example: $0 /dev/disk1s4 /System/Volumes/Update/mnt1"
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    # Running as root, mount directly
    /sbin/mount -o nobrowse -t apfs "$DEVICE" "$MOUNTPOINT"
else
    # Check if sudo is available and configured for passwordless mount
    if sudo -n /sbin/mount -o nobrowse -t apfs "$DEVICE" "$MOUNTPOINT" 2>/dev/null; then
        echo "Successfully mounted $DEVICE to $MOUNTPOINT"
        exit 0
    fi
    
    # If passwordless sudo fails, try with password prompt
    echo "Attempting to mount with sudo..."
    if sudo /sbin/mount -o nobrowse -t apfs "$DEVICE" "$MOUNTPOINT"; then
        echo "Successfully mounted $DEVICE to $MOUNTPOINT"
    else
        echo "Failed to mount $DEVICE to $MOUNTPOINT"
        echo "You may need to:"
        echo "1. Run this script as root"
        echo "2. Configure sudo to allow passwordless mounting"
        echo "3. Provide sudo password when prompted"
        exit 1
    fi
fi