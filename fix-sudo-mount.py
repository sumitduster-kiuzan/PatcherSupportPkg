#!/usr/bin/env python3

"""
Fix Sudo Mount Password Issue

This script helps resolve the sudo password issue when mounting volumes
for OpenCore Legacy Patcher by configuring temporary passwordless sudo
access for mount-related commands.
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path


class SudoMountFixer:
    
    def __init__(self):
        self.username = getpass.getuser()
        self.sudoers_file = Path("/etc/sudoers.d/oclp-mount")
        self.sudoers_entry = f"{self.username} ALL=(ALL) NOPASSWD: /sbin/mount, /sbin/umount, /usr/sbin/diskutil, /usr/bin/hdiutil"
    
    def is_root(self) -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    def check_sudo_access(self) -> bool:
        """Check if user has sudo access"""
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
    
    def configure_passwordless_mount(self) -> bool:
        """Configure passwordless sudo for mount commands"""
        if not self.is_root():
            print("❌ This function requires root privileges.")
            print("Please run: sudo python3 fix-sudo-mount.py --configure")
            return False
        
        try:
            # Create sudoers entry
            with open(self.sudoers_file, 'w') as f:
                f.write(f"{self.sudoers_entry}\n")
            
            # Set correct permissions
            os.chmod(self.sudoers_file, 0o440)
            
            print("✅ Successfully configured passwordless mounting")
            print(f"   Created: {self.sudoers_file}")
            print(f"   User: {self.username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure passwordless mounting: {e}")
            return False
    
    def remove_configuration(self) -> bool:
        """Remove the sudo configuration"""
        if not self.is_root():
            print("❌ This function requires root privileges.")
            print("Please run: sudo python3 fix-sudo-mount.py --remove")
            return False
        
        try:
            if self.sudoers_file.exists():
                self.sudoers_file.unlink()
                print("✅ Successfully removed sudo configuration")
            else:
                print("⚠️  No sudo configuration found to remove")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove configuration: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test if mount commands work without password"""
        print("🧪 Testing sudo mount configuration...")
        
        # Test if we can run mount without password
        try:
            result = subprocess.run(
                ["sudo", "-n", "/sbin/mount"],
                capture_output=True,
                timeout=5
            )
            
            # mount without arguments should fail with usage info, not permission error
            if result.returncode != 0:
                stderr = result.stderr.decode('utf-8').lower()
                if "password" in stderr or "terminal is required" in stderr:
                    print("❌ Mount commands still require password")
                    return False
                else:
                    print("✅ Mount commands work without password")
                    return True
            else:
                print("✅ Mount commands work without password")
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️  Mount command test timed out")
            return False
        except Exception as e:
            print(f"❌ Error testing mount configuration: {e}")
            return False
    
    def show_status(self):
        """Show current status"""
        print("📊 Current Status:")
        print(f"   User: {self.username}")
        print(f"   Running as root: {'Yes' if self.is_root() else 'No'}")
        print(f"   Sudo access: {'Yes' if self.check_sudo_access() else 'No'}")
        print(f"   Config file exists: {'Yes' if self.sudoers_file.exists() else 'No'}")
        
        if self.sudoers_file.exists():
            try:
                with open(self.sudoers_file, 'r') as f:
                    content = f.read().strip()
                print(f"   Config content: {content}")
            except PermissionError:
                print("   Config content: <Permission denied>")
    
    def show_usage(self):
        """Show usage information"""
        print("Usage: python3 fix-sudo-mount.py [OPTION]")
        print()
        print("Options:")
        print("  --configure    Configure passwordless mounting (requires sudo)")
        print("  --remove       Remove configuration (requires sudo)")
        print("  --test         Test current configuration")
        print("  --status       Show current status")
        print("  --help         Show this help")
        print()
        print("Examples:")
        print("  sudo python3 fix-sudo-mount.py --configure")
        print("  python3 fix-sudo-mount.py --test")
        print("  sudo python3 fix-sudo-mount.py --remove")


def main():
    fixer = SudoMountFixer()
    
    if len(sys.argv) < 2:
        print("⚠️  No option specified")
        fixer.show_usage()
        return
    
    option = sys.argv[1]
    
    if option == "--configure":
        success = fixer.configure_passwordless_mount()
        if success:
            print("\n🎉 Configuration complete! You should now be able to mount volumes without password prompts.")
            print("💡 Run 'python3 fix-sudo-mount.py --test' to verify the configuration.")
            print("🧹 Don't forget to run 'sudo python3 fix-sudo-mount.py --remove' when done.")
    
    elif option == "--remove":
        fixer.remove_configuration()
    
    elif option == "--test":
        if fixer.test_configuration():
            print("🎉 Mount configuration is working correctly!")
        else:
            print("💡 Run 'sudo python3 fix-sudo-mount.py --configure' to set up passwordless mounting.")
    
    elif option == "--status":
        fixer.show_status()
    
    elif option == "--help":
        fixer.show_usage()
    
    else:
        print(f"❌ Unknown option: {option}")
        fixer.show_usage()


if __name__ == "__main__":
    main()