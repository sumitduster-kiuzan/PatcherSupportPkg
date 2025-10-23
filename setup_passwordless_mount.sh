#!/bin/bash

# Setup script for passwordless mounting
# This script configures sudo to allow mounting without a password

set -e

echo "Setting up passwordless mounting..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

# Create sudoers file for mount operations
SUDOERS_FILE="/etc/sudoers.d/mount"

echo "Creating sudoers configuration..."

# Create the sudoers file
cat > "$SUDOERS_FILE" << 'EOF'
# Allow passwordless mounting for admin users
%admin ALL=(ALL) NOPASSWD: /sbin/mount
%admin ALL=(ALL) NOPASSWD: /sbin/umount
%admin ALL=(ALL) NOPASSWD: /usr/sbin/diskutil
EOF

# Set proper permissions
chmod 440 "$SUDOERS_FILE"

# Verify the configuration
echo "Verifying sudoers configuration..."
visudo -c -f "$SUDOERS_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Sudoers configuration created successfully"
    echo "✓ Passwordless mounting is now enabled for admin users"
    echo ""
    echo "You can now run mount commands without a password:"
    echo "  sudo /sbin/mount -o nobrowse -t apfs /dev/disk1s4 /System/Volumes/Update/mnt1"
else
    echo "✗ Sudoers configuration is invalid"
    echo "Removing invalid configuration..."
    rm -f "$SUDOERS_FILE"
    exit 1
fi

echo ""
echo "Note: You may need to log out and log back in for the changes to take effect."