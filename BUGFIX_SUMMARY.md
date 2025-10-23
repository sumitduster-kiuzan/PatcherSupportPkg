# Bug Fix: Root Volume Mount String Decode Error

## Summary
Fixed `AttributeError: 'str' object has no attribute 'decode'` in OpenCore Legacy Patcher that occurred during root volume mounting for system patching.

## Error Details
- **Error:** `AttributeError: 'str' object has no attribute 'decode'`
- **File:** `opencore_legacy_patcher/support/subprocess_wrapper.py`
- **Lines:** 122, 127 (in `generate_log()` function)
- **Trigger:** Occurs during system patching when mounting root volume

### Full Traceback
```
File "opencore_legacy_patcher/wx_gui/gui_sys_patch_start.py", line 340, in _start_root_patching
File "opencore_legacy_patcher/sys_patch/sys_patch.py", line 572, in start_patch
File "opencore_legacy_patcher/sys_patch/sys_patch.py", line 127, in _mount_root_vol
File "opencore_legacy_patcher/sys_patch/mount/mount.py", line 113, in mount
File "opencore_legacy_patcher/sys_patch/mount/mount.py", line 73, in _mount_root_volume
File "opencore_legacy_patcher/support/subprocess_wrapper.py", line 141, in log
File "opencore_legacy_patcher/support/subprocess_wrapper.py", line 177, in generate_log
AttributeError: 'str' object has no attribute 'decode'
```

## Root Cause
The `generate_log()` function in `subprocess_wrapper.py` always attempts to decode subprocess output using `.decode("utf-8")`, assuming the output is a `bytes` object. However, `process.stdout` and `process.stderr` can sometimes already be `str` objects (depending on Python version, subprocess configuration, or system settings), which causes the AttributeError.

## Solution
Added a type-safe helper function `__decode_output()` that checks whether the output is bytes or string before attempting to decode:

```python
def __decode_output(output) -> str:
    """
    Decode subprocess output to string.
    Handles both bytes and str types.
    """
    if isinstance(output, bytes):
        return output.decode("utf-8")
    return output
```

This function is now used in `generate_log()` instead of directly calling `.decode()`.

## Changes Made

### File: `opencore_legacy_patcher/support/subprocess_wrapper.py`

1. **Added new helper function** (lines 134-141):
   ```python
   def __decode_output(output) -> str:
       """
       Decode subprocess output to string.
       Handles both bytes and str types.
       """
       if isinstance(output, bytes):
           return output.decode("utf-8")
       return output
   ```

2. **Modified `generate_log()` function**:
   - Line 122: Changed from `process.stdout.decode("utf-8")` to `__decode_output(process.stdout)`
   - Line 127: Changed from `process.stderr.decode("utf-8")` to `__decode_output(process.stderr)`

## Testing
✅ Tested with bytes input (original behavior)
✅ Tested with string input (bug scenario)
✅ Tested with None input
✅ Tested with UTF-8 encoded special characters

All tests passed successfully.

## How to Apply

### Option 1: Apply the patch
```bash
cd /path/to/OpenCore-Legacy-Patcher
patch -p1 < /path/to/subprocess_wrapper_decode_fix.patch
```

### Option 2: Manual edit
Edit `opencore_legacy_patcher/support/subprocess_wrapper.py`:
1. Add the `__decode_output()` function before `__resolve_privileged_helper_errors()`
2. Replace the two `.decode("utf-8")` calls with `__decode_output()` calls in `generate_log()`

## Impact
- **Before:** System patching would crash when attempting to mount root volume
- **After:** System patching handles both bytes and string subprocess output gracefully

## Repository Note
This fix applies to the **OpenCore-Legacy-Patcher** repository (https://github.com/dortania/OpenCore-Legacy-Patcher), not the PatcherSupportPkg repository.

## Patch File
The patch file is available at: `subprocess_wrapper_decode_fix.patch`

---
**Date:** 2025-10-23
**Status:** ✅ Fix Complete and Tested
