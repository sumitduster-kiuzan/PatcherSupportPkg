#!/bin/bash
# Configure passwordless sudo for mount/umount commands
# This is required for automated mounting of the Universal-Binaries.dmg

set -e

echo "==================================="
echo "Configure Passwordless Sudo for Mounting"
echo "==================================="
echo ""

# Get the current username
CURRENT_USER=$(whoami)

echo "This script will configure passwordless sudo for mount/umount commands"
echo "for user: $CURRENT_USER"
echo ""
echo "Commands that will be allowed without password:"
echo "  - /sbin/mount"
echo "  - /sbin/umount"
echo "  - /usr/sbin/diskutil"
echo ""

# Prompt for confirmation
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create the sudoers configuration
SUDOERS_FILE="/etc/sudoers.d/oclp-mount"
SUDOERS_CONTENT="$CURRENT_USER ALL=(ALL) NOPASSWD: /sbin/mount, /sbin/umount, /usr/sbin/diskutil, /usr/bin/hdiutil"

echo ""
echo "Creating sudoers configuration..."
echo "File: $SUDOERS_FILE"
echo "Content: $SUDOERS_CONTENT"
echo ""

# Write the sudoers file (requires sudo)
echo "$SUDOERS_CONTENT" | sudo tee "$SUDOERS_FILE" > /dev/null

# Set correct permissions
sudo chmod 0440 "$SUDOERS_FILE"

# Validate the sudoers file
if sudo visudo -c -f "$SUDOERS_FILE"; then
    echo ""
    echo "✓ Sudoers configuration successfully created and validated!"
    echo ""
    echo "You can now run mount/umount commands without entering a password."
    echo ""
    echo "To test, try:"
    echo "  sudo mount --help"
    echo ""
else
    echo ""
    echo "✗ ERROR: Sudoers file validation failed!"
    echo "Removing the invalid configuration..."
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi

echo "To remove this configuration later, run:"
echo "  sudo rm $SUDOERS_FILE"
