# OpenCore Legacy Patcher Privileged Helper Fix

## Issue Description

The OpenCore Legacy Patcher is encountering a `FileNotFoundError` when trying to execute a privileged helper tool:

```
FileNotFoundError: [Errno 2] No such file or directory: '/Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper'
```

This error occurs in the patcher's root patching process when it tries to mount the root volume for system modifications.

## Root Cause

The privileged helper tool `com.sumitduster.opencore-legacy-patcher.privileged-helper` is not installed on the system. This tool is required for the patcher to perform root-level operations safely.

## Solutions

### Solution 1: Reinstall OpenCore Legacy Patcher (Recommended)

1. **Download the latest version** of OpenCore Legacy Patcher from the official repository
2. **Run the installer** which should properly install the privileged helper tool
3. **Grant necessary permissions** when prompted by macOS

### Solution 2: Manual Privileged Helper Installation

If you have the patcher source code, you can manually install the privileged helper:

1. **Locate the privileged helper** in the patcher's resources
2. **Copy the helper tool** to `/Library/PrivilegedHelperTools/`
3. **Set proper permissions**:
   ```bash
   sudo chown root:wheel /Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper
   sudo chmod 755 /Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper
   ```
4. **Register the helper** with the system (if required)

### Solution 3: Check System Integrity

1. **Verify SIP status**:
   ```bash
   csrutil status
   ```
2. **Check for system modifications** that might interfere with privileged operations
3. **Ensure you're running as administrator** when using the patcher

### Solution 4: Alternative Root Patching Method

If the privileged helper continues to cause issues:

1. **Use the patcher's GUI** instead of command-line operations
2. **Try running with sudo** (though this may not work for GUI applications)
3. **Check if there are alternative patching methods** in the patcher's documentation

## Prevention

To prevent this issue in the future:

1. **Always use the official installer** rather than running from source
2. **Keep the patcher updated** to the latest version
3. **Don't manually modify** system files that the patcher manages
4. **Backup your system** before making any modifications

## Additional Notes

- This repository (PatcherSupportPkg) contains the binary resources for OpenCore Legacy Patcher
- The actual patcher code is in a separate repository
- The privileged helper is typically installed as part of the main patcher application
- If you're developing or testing, ensure you have the complete patcher setup, not just the support package

## Related Files

The error originates from:
- `opencore_legacy_patcher/support/subprocess_wrapper.py` (line 54)
- `opencore_legacy_patcher/sys_patch/mount/mount.py` (line 70)
- `opencore_legacy_patcher/sys_patch/sys_patch.py` (line 127)

These files are part of the main OpenCore Legacy Patcher repository, not this PatcherSupportPkg repository.