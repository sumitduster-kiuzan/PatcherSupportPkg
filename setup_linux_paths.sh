#!/bin/bash
# Setup script to create symbolic links for OpenCore Legacy Patcher on Linux
# This script maps macOS temporary paths to the actual Universal-Binaries location

set -e

echo "Setting up Linux path mapping for OpenCore Legacy Patcher..."

# Create the base temporary directory structure
TEMP_BASE="/var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf/payloads"
UNIVERSAL_BINARIES="/workspace/Universal-Binaries"

# Create directory structure
sudo mkdir -p "$TEMP_BASE/Universal-Binaries"

# Find all directories in Universal-Binaries that contain usr/libexec
find "$UNIVERSAL_BINARIES" -name "usr" -type d | while read usr_dir; do
    version_dir=$(dirname "$usr_dir")
    version_name=$(basename "$version_dir")
    
    echo "Setting up links for version: $version_name"
    
    # Create the target directory structure
    target_dir="$TEMP_BASE/Universal-Binaries/$version_name"
    sudo mkdir -p "$target_dir"
    
    # Create symbolic link for the entire usr directory
    sudo ln -sf "$usr_dir" "$target_dir/usr"
    
    echo "  Created link: $target_dir/usr -> $usr_dir"
done

echo "Setup complete! The patcher should now be able to find the required files."
echo "Note: This is a workaround for running macOS software on Linux."
echo "For production use, run the patcher on macOS."