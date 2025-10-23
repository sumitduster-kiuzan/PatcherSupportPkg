#!/usr/bin/env python3
"""
Mount helper script to handle sudo password issues
Usage: python3 mount_helper.py <device> <mountpoint>
"""

import sys
import subprocess
import os
import getpass
from pathlib import Path


def run_command(cmd, input_data=None, check=True):
    """Run a command with proper error handling"""
    try:
        result = subprocess.run(
            cmd, 
            input=input_data, 
            text=True, 
            capture_output=True, 
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def mount_with_sudo(device, mountpoint, password=None):
    """Attempt to mount using sudo with various methods"""
    
    mount_cmd = ["sudo", "/sbin/mount", "-o", "nobrowse", "-t", "apfs", device, mountpoint]
    
    # Method 1: Try passwordless sudo first
    print("Attempting passwordless sudo...")
    success, stdout, stderr = run_command(mount_cmd, check=False)
    if success:
        print("✓ Successfully mounted with passwordless sudo")
        return True
    
    # Method 2: Try with password from stdin
    if password:
        print("Attempting sudo with provided password...")
        success, stdout, stderr = run_command(mount_cmd, input_data=password, check=False)
        if success:
            print("✓ Successfully mounted with password")
            return True
    
    # Method 3: Try interactive sudo
    print("Attempting interactive sudo...")
    try:
        result = subprocess.run(mount_cmd, check=False)
        if result.returncode == 0:
            print("✓ Successfully mounted with interactive sudo")
            return True
    except Exception as e:
        print(f"Interactive sudo failed: {e}")
    
    return False


def mount_as_root(device, mountpoint):
    """Attempt to mount as root"""
    mount_cmd = ["/sbin/mount", "-o", "nobrowse", "-t", "apfs", device, mountpoint]
    
    print("Attempting direct mount as root...")
    success, stdout, stderr = run_command(mount_cmd, check=False)
    if success:
        print("✓ Successfully mounted as root")
        return True
    
    print(f"✗ Direct mount failed: {stderr}")
    return False


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 mount_helper.py <device> <mountpoint>")
        print("Example: python3 mount_helper.py /dev/disk1s4 /System/Volumes/Update/mnt1")
        sys.exit(1)
    
    device = sys.argv[1]
    mountpoint = sys.argv[2]
    
    print(f"Attempting to mount {device} to {mountpoint}")
    
    # Check if running as root
    if os.geteuid() == 0:
        print("Running as root")
        if mount_as_root(device, mountpoint):
            sys.exit(0)
    else:
        print("Running as regular user")
        
        # Try to get password if not provided
        password = None
        try:
            password = getpass.getpass("Enter sudo password (or press Enter to skip): ")
            if not password.strip():
                password = None
        except KeyboardInterrupt:
            print("\nCancelled by user")
            sys.exit(1)
        
        if mount_with_sudo(device, mountpoint, password):
            sys.exit(0)
    
    print("\n✗ All mount attempts failed")
    print("\nTroubleshooting suggestions:")
    print("1. Run this script as root: sudo python3 mount_helper.py <device> <mountpoint>")
    print("2. Configure sudo for passwordless mounting:")
    print("   echo '%admin ALL=(ALL) NOPASSWD: /sbin/mount' | sudo tee /etc/sudoers.d/mount")
    print("3. Check if the device exists: ls -la /dev/disk*")
    print("4. Check if the mountpoint exists: ls -la /System/Volumes/Update/")
    print("5. Check if the device is already mounted: mount | grep apfs")
    
    sys.exit(1)


if __name__ == "__main__":
    main()