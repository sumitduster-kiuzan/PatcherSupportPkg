# OpenCore Legacy Patcher Privileged Helper Tool

This directory contains the privileged helper tool for OpenCore Legacy Patcher that provides elevated system access for mounting, file operations, and other administrative tasks.

## Problem Solved

This fixes the error:
```
FileNotFoundError: [Errno 2] No such file or directory: '/Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper'
```

## Files

- `privileged-helper.c` - Source code for the privileged helper tool
- `com.sumitduster.opencore-legacy-patcher.privileged-helper.plist` - LaunchDaemon configuration
- `Makefile` - Build configuration
- `install-privileged-helper.sh` - Installation script
- `uninstall-privileged-helper.sh` - Uninstallation script

## Installation

### Automatic Installation (Recommended)

1. Run the installation script as root:
   ```bash
   sudo ./install-privileged-helper.sh
   ```

### Manual Installation

1. Build the helper tool:
   ```bash
   make build
   ```

2. Install manually:
   ```bash
   sudo make install
   ```

## Features

The privileged helper tool supports the following operations via XPC:

- **Mount operations**: Mount disk images and volumes
- **Unmount operations**: Unmount volumes with optional force flag
- **File operations**: Copy, move, delete files and directories with root privileges
- **Command execution**: Execute system commands with elevated privileges

## Usage

The helper tool is automatically invoked by OpenCore Legacy Patcher when root privileges are required. It communicates via XPC (inter-process communication) and runs as a LaunchDaemon with root privileges.

## Uninstallation

To remove the privileged helper tool:

```bash
sudo ./uninstall-privileged-helper.sh
```

Or manually:

```bash
sudo make uninstall
```

## Security

- The helper tool runs with root privileges only when needed
- It's configured as an on-demand LaunchDaemon (not always running)
- All operations are validated before execution
- Communication is handled through secure XPC messaging

## Troubleshooting

### Check if the helper is loaded:
```bash
sudo launchctl list | grep com.sumitduster.opencore-legacy-patcher.privileged-helper
```

### View logs:
```bash
sudo tail -f /var/log/opencore-legacy-patcher-privileged-helper.log
```

### Reload the helper:
```bash
sudo make reload
```

## Requirements

- macOS 10.13 or later
- Xcode command line tools (for building)
- Administrator privileges (for installation)

## Build Requirements

- clang compiler
- XPC framework
- Foundation framework
- Security framework