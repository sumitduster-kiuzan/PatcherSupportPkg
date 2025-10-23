#!/bin/bash

# Fix for missing OpenCore Legacy Patcher privileged helper
# This script helps diagnose and potentially fix the missing privileged helper issue

set -e

PRIVILEGED_HELPER_PATH="/Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper"
HELPER_DIR="/Library/PrivilegedHelperTools"

echo "OpenCore Legacy Patcher Privileged Helper Fix"
echo "=============================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   echo "Usage: sudo ./fix-privileged-helper.sh"
   exit 1
fi

echo "Checking privileged helper status..."
echo ""

# Check if the privileged helper directory exists
if [ ! -d "$HELPER_DIR" ]; then
    echo "Creating PrivilegedHelperTools directory..."
    mkdir -p "$HELPER_DIR"
    chmod 755 "$HELPER_DIR"
    echo "✓ Created $HELPER_DIR"
else
    echo "✓ PrivilegedHelperTools directory exists"
fi

# Check if the specific privileged helper exists
if [ -f "$PRIVILEGED_HELPER_PATH" ]; then
    echo "✓ Privileged helper exists at $PRIVILEGED_HELPER_PATH"
    echo "  File permissions: $(ls -la "$PRIVILEGED_HELPER_PATH")"
    echo "  File type: $(file "$PRIVILEGED_HELPER_PATH")"
else
    echo "✗ Privileged helper missing at $PRIVILEGED_HELPER_PATH"
    echo ""
    echo "This is the root cause of your error. The OpenCore Legacy Patcher"
    echo "application is trying to execute this privileged helper but it doesn't exist."
    echo ""
    echo "Possible solutions:"
    echo "1. Reinstall OpenCore Legacy Patcher from the official source"
    echo "2. Check if the privileged helper was not properly installed during setup"
    echo "3. Look for the privileged helper in the OpenCore Legacy Patcher application bundle"
    echo ""
    
    # Try to find the privileged helper in common locations
    echo "Searching for privileged helper in common locations..."
    echo ""
    
    # Search in Applications
    if [ -d "/Applications" ]; then
        echo "Searching in /Applications..."
        find /Applications -name "*opencore*" -type d 2>/dev/null | while read -r app_dir; do
            echo "  Found: $app_dir"
            find "$app_dir" -name "*privileged-helper*" 2>/dev/null | while read -r helper; do
                echo "    Found privileged helper: $helper"
            done
        done
    fi
    
    # Search in user's home directory
    echo "Searching in user home directories..."
    for user_home in /Users/*; do
        if [ -d "$user_home" ]; then
            username=$(basename "$user_home")
            echo "  Checking $username's home directory..."
            find "$user_home" -name "*opencore*" -type d 2>/dev/null | while read -r app_dir; do
                echo "    Found: $app_dir"
                find "$app_dir" -name "*privileged-helper*" 2>/dev/null | while read -r helper; do
                    echo "      Found privileged helper: $helper"
                done
            done
        fi
    done
    
    echo ""
    echo "If you found the privileged helper in one of the above locations,"
    echo "you can copy it to the correct location with:"
    echo "  sudo cp /path/to/found/privileged-helper $PRIVILEGED_HELPER_PATH"
    echo "  sudo chmod +x $PRIVILEGED_HELPER_PATH"
    echo ""
fi

# Check for any existing privileged helper tools
echo "Checking for other privileged helper tools..."
if [ -d "$HELPER_DIR" ]; then
    helper_count=$(find "$HELPER_DIR" -type f | wc -l)
    if [ "$helper_count" -gt 0 ]; then
        echo "Found $helper_count privileged helper(s):"
        ls -la "$HELPER_DIR"
    else
        echo "No privileged helpers found in $HELPER_DIR"
    fi
fi

echo ""
echo "Additional troubleshooting steps:"
echo "1. Check if OpenCore Legacy Patcher is properly installed"
echo "2. Try reinstalling OpenCore Legacy Patcher"
echo "3. Check the OpenCore Legacy Patcher documentation for privileged helper setup"
echo "4. Ensure you have the latest version of OpenCore Legacy Patcher"
echo ""
echo "For more help, visit: https://github.com/dortania/OpenCore-Legacy-Patcher"