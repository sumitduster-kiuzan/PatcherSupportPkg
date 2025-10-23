# OpenCore Legacy Patcher Linux Setup

## Problem

The OpenCore Legacy Patcher is designed to run on macOS and expects files to be available in macOS-style temporary directory paths (e.g., `/var/folders/.../T/tmp.../payloads/Universal-Binaries/...`). When running on Linux, these paths don't exist, causing errors like:

```
Exception: Failed to find /var/folders/wg/grjdr12s121cxm1r6tv6lm4h0000gn/T/tmp0w61edtf/payloads/Universal-Binaries/13.7.2-25/usr/libexec/airportd
```

## Solution

This repository includes scripts to create symbolic links that map the expected macOS temporary paths to the actual file locations in the workspace.

## Setup

### Using the Default Path

If you're getting the error with the default temporary path, simply run:

```bash
./setup_linux_paths.sh
```

### Using a Custom Path

If your error shows a different temporary path, extract the path from the error message and pass it as an argument. For example, if the error shows:

```
Exception: Failed to find /var/folders/xx/yyyyyyyy/T/tmpABCDEF/payloads/Universal-Binaries/...
```

Run the setup script with the temp directory path (everything up to but not including `/payloads`):

```bash
./setup_linux_paths.sh "/var/folders/xx/yyyyyyyy/T/tmpABCDEF"
```

### What the Script Does

The setup script will:
1. Create the required directory structure in the temporary location
2. Create symbolic links for all files in Universal-Binaries
3. Map the expected paths to the actual Universal-Binaries location
4. Preserve the directory structure expected by OCLP

## Cleanup

To remove the symbolic links and temporary directories:

```bash
./cleanup_linux_paths.sh
```

Or, if you used a custom path:

```bash
./cleanup_linux_paths.sh "/var/folders/xx/yyyyyyyy/T/tmpABCDEF"
```

## Important Notes

- **This is a workaround** for running macOS software on Linux
- For production use, run the OpenCore Legacy Patcher on macOS
- The symbolic links will persist until manually cleaned up
- **Requires sudo access** to create directories in `/var/folders`
- The temporary path is randomly generated each time OCLP runs, so you may need to run setup again with a new path

## Troubleshooting

### Error: Permission Denied

If you get permission errors, make sure you have sudo privileges:

```bash
sudo ./setup_linux_paths.sh
```

### Error: Directory Already Exists

If the directory already exists from a previous run, clean it up first:

```bash
./cleanup_linux_paths.sh
./setup_linux_paths.sh
```

### Error: Universal-Binaries Not Found

Make sure you're running the script from the PatcherSupportPkg directory:

```bash
cd /path/to/PatcherSupportPkg
./setup_linux_paths.sh
```

## Alternative: Fix in OpenCore Legacy Patcher

For a more permanent solution, the OpenCore Legacy Patcher code should be modified to:
1. Handle missing files gracefully
2. Support configurable payload paths
3. Work with relative paths instead of absolute temporary paths

This would eliminate the need for this workaround.

## Files in This Solution

- `setup_linux_paths.sh` - Creates symbolic links for all required paths
- `cleanup_linux_paths.sh` - Removes the symbolic links and temporary directories
- `LINUX_SETUP_README.md` - This documentation file
