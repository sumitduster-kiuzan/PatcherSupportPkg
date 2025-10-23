# OpenCore Legacy Patcher Linux Setup

## Problem
The OpenCore Legacy Patcher is designed to run on macOS and expects files to be available in macOS-style temporary directory paths (e.g., `/var/folders/...`). When running on Linux, these paths don't exist, causing the error:

```
Exception: Failed to find /var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf/payloads/Universal-Binaries/13.7.2-25/usr/libexec/airportd
```

## Solution
This repository includes scripts to create symbolic links that map the expected macOS paths to the actual file locations in the workspace.

## Setup
Run the setup script to create all necessary symbolic links:

```bash
./setup_linux_paths.sh
```

This script will:
1. Create the required directory structure in `/var/folders/...`
2. Create symbolic links for all macOS versions that have `usr/libexec` directories
3. Map the expected paths to the actual Universal-Binaries location

## Cleanup
To remove the symbolic links and temporary directories:

```bash
./cleanup_linux_paths.sh
```

## Important Notes
- This is a workaround for running macOS software on Linux
- For production use, run the OpenCore Legacy Patcher on macOS
- The symbolic links will persist until manually cleaned up
- This solution only works if you have sudo access

## Files Created
- `setup_linux_paths.sh` - Creates symbolic links for all required paths
- `cleanup_linux_paths.sh` - Removes the symbolic links and temporary directories
- `LINUX_SETUP_README.md` - This documentation file