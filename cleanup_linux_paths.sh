#!/bin/bash
# Cleanup script to remove symbolic links created for OpenCore Legacy Patcher on Linux

set -e

# Parse command line arguments
TEMP_PATH=""
if [ $# -eq 1 ]; then
    TEMP_PATH="$1"
fi

# If no argument provided, try to use the standard temp path
if [ -z "$TEMP_PATH" ]; then
    TEMP_PATH="/var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf"
fi

echo "Cleaning up Linux path mapping for OpenCore Legacy Patcher..."
echo "Temporary path: $TEMP_PATH"

# Check if the temporary directory exists
if [ -d "$TEMP_PATH" ]; then
    echo "Removing temporary directory: $TEMP_PATH"
    sudo rm -rf "$TEMP_PATH"
    echo "Cleanup complete!"
else
    echo "No temporary directory found at $TEMP_PATH"
fi

# Also clean up common parent directories if they're empty
PARENT_DIR="$(dirname "$TEMP_PATH")"
while [ "$PARENT_DIR" != "/" ] && [ "$PARENT_DIR" != "/var" ]; do
    if [ -d "$PARENT_DIR" ] && [ -z "$(ls -A "$PARENT_DIR" 2>/dev/null)" ]; then
        echo "Removing empty parent directory: $PARENT_DIR"
        sudo rmdir "$PARENT_DIR" 2>/dev/null || break
        PARENT_DIR="$(dirname "$PARENT_DIR")"
    else
        break
    fi
done

echo "All cleanup operations complete."
