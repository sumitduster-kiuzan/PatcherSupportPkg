#!/bin/bash
# Setup script to create symbolic links for OpenCore Legacy Patcher on Linux
# This script maps macOS temporary paths to the actual Universal-Binaries location

set -e

# Parse command line arguments
TEMP_PATH=""
if [ $# -eq 1 ]; then
    TEMP_PATH="$1"
fi

# If no argument provided, try to use the standard temp path from the error
if [ -z "$TEMP_PATH" ]; then
    TEMP_PATH="/var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf"
fi

echo "Setting up Linux path mapping for OpenCore Legacy Patcher..."
echo "Temporary path: $TEMP_PATH"

# Get the workspace directory (where this script is located)
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIVERSAL_BINARIES="$WORKSPACE_DIR/Universal-Binaries"

if [ ! -d "$UNIVERSAL_BINARIES" ]; then
    echo "Error: Universal-Binaries directory not found at $UNIVERSAL_BINARIES"
    exit 1
fi

# Create the base temporary directory structure
TEMP_BASE="$TEMP_PATH/payloads"

echo "Creating directory structure: $TEMP_BASE/Universal-Binaries"
sudo mkdir -p "$TEMP_BASE/Universal-Binaries"

# Find all directories in Universal-Binaries and create appropriate links
for version_dir in "$UNIVERSAL_BINARIES"/*; do
    if [ ! -d "$version_dir" ]; then
        continue
    fi
    
    version_name=$(basename "$version_dir")
    target_dir="$TEMP_BASE/Universal-Binaries/$version_name"
    
    echo "Setting up links for version: $version_name"
    
    # Create the target directory
    sudo mkdir -p "$target_dir"
    
    # Link the entire version directory contents
    for item in "$version_dir"/*; do
        item_name=$(basename "$item")
        if [ ! -e "$target_dir/$item_name" ]; then
            sudo ln -sf "$item" "$target_dir/$item_name"
            echo "  Created link: $target_dir/$item_name -> $item"
        fi
    done
done

echo ""
echo "Setup complete! The patcher should now be able to find the required files."
echo "To clean up, run: ./cleanup_linux_paths.sh \"$TEMP_PATH\""
echo ""
echo "Note: This is a workaround for running macOS software on Linux."
echo "For production use, run the patcher on macOS."
