# Troubleshooting Guide

## Sudo Mount Password Issue

### Problem Description

When mounting the `Universal-Binaries.dmg` in automated or CI/CD environments, you may encounter the following error:

```
Failed to mount root volume
Subprocess failed.
    Command: ['sudo', '/sbin/mount', '-o', 'nobrowse', '-t', 'apfs', '/dev/disk1s4', '/System/Volumes/Update/mnt1']
    Return Code: 1
    Standard Output:
        sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
        sudo: a password is required
```

This occurs because the mount operation requires `sudo` privileges, but there's no interactive terminal available to enter the password.

### Quick Fix

Run the provided configuration script to set up passwordless sudo for mount operations:

```bash
./configure-passwordless-sudo.sh
```

This script will:
1. Create a sudoers configuration file at `/etc/sudoers.d/oclp-mount`
2. Allow your user to run mount/umount/diskutil commands without a password
3. Validate the configuration to ensure it's correct

### Manual Configuration

If you prefer to configure manually, follow the detailed instructions in [SUDO_MOUNT_FIX.md](./SUDO_MOUNT_FIX.md).

### Security Considerations

The passwordless sudo configuration is scoped to only these specific commands:
- `/sbin/mount`
- `/sbin/umount`
- `/usr/sbin/diskutil`
- `/usr/bin/hdiutil`

This minimizes security risk while allowing the necessary operations for mounting the DMG.

### For CI/CD Environments

In CI/CD environments (GitHub Actions, GitLab CI, etc.), you should:
1. Configure passwordless sudo during the environment setup phase
2. Never store passwords in scripts or environment variables
3. Use the provided configuration script in your CI workflow

Example for GitHub Actions:
```yaml
- name: Configure passwordless sudo for mount
  run: |
    echo "$USER ALL=(ALL) NOPASSWD: /sbin/mount, /sbin/umount, /usr/sbin/diskutil, /usr/bin/hdiutil" | sudo tee /etc/sudoers.d/oclp-mount
    sudo chmod 0440 /etc/sudoers.d/oclp-mount
```

### Alternative Solutions

If you cannot configure passwordless sudo, consider these alternatives:

1. **Use sudo -S with password input**: See [SUDO_MOUNT_FIX.md](./SUDO_MOUNT_FIX.md) for implementation details
2. **Use SUDO_ASKPASS**: Configure an askpass helper program (see documentation)
3. **Run as root**: If in a containerized environment, run the entire process as root (not recommended for production)

### Verifying the Fix

After configuration, test that mount commands work without a password prompt:

```bash
sudo mount --help
```

If no password is requested, the configuration is working correctly.

### Removing the Configuration

If you need to remove the passwordless sudo configuration:

```bash
sudo rm /etc/sudoers.d/oclp-mount
```

## Other Common Issues

### DMG Creation Fails with "Resource busy"

If DMG creation fails with a "Resource busy" error, the scripts will automatically attempt to reset `hdiutil` and retry. If the problem persists:

```bash
killall hdiutil
sudo diskutil unmountDisk force /dev/diskX  # Replace X with the appropriate disk number
```

### Codesigning Failures

If you encounter codesigning failures during CI runs, ensure:
1. The signing identity is correctly installed
2. Files are properly adhoc-signed before committing
3. Pre-existing Apple-signed binaries are not being modified

For more details, see the comments in [ci.py](./ci.py).
