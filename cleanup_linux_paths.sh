#!/bin/bash
# Cleanup script to remove symbolic links created for OpenCore Legacy Patcher on Linux

echo "Cleaning up Linux path mapping for OpenCore Legacy Patcher..."

# Remove the temporary directory structure
TEMP_BASE="/var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf"

if [ -d "$TEMP_BASE" ]; then
    echo "Removing temporary directory: $TEMP_BASE"
    sudo rm -rf "$TEMP_BASE"
    echo "Cleanup complete!"
else
    echo "No temporary directory found to clean up."
fi