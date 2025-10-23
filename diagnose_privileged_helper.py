#!/usr/bin/env python3
"""
Diagnose and help fix missing OpenCore Legacy Patcher privileged helper issue.

This script helps diagnose the FileNotFoundError related to the missing
privileged helper tool at /Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Tuple


class PrivilegedHelperDiagnostic:
    """Diagnose and help fix missing privileged helper issues."""
    
    def __init__(self):
        self.helper_path = "/Library/PrivilegedHelperTools/com.sumitduster.opencore-legacy-patcher.privileged-helper"
        self.helper_dir = "/Library/PrivilegedHelperTools"
        self.is_root = os.geteuid() == 0
        
    def check_root_permissions(self) -> bool:
        """Check if running with root permissions."""
        if not self.is_root:
            print("❌ This script must be run as root (use sudo)")
            print("Usage: sudo python3 diagnose_privileged_helper.py")
            return False
        print("✅ Running with root permissions")
        return True
    
    def check_helper_directory(self) -> bool:
        """Check if the PrivilegedHelperTools directory exists."""
        if not os.path.exists(self.helper_dir):
            print(f"❌ PrivilegedHelperTools directory missing: {self.helper_dir}")
            return False
        print(f"✅ PrivilegedHelperTools directory exists: {self.helper_dir}")
        return True
    
    def check_privileged_helper(self) -> bool:
        """Check if the specific privileged helper exists."""
        if not os.path.exists(self.helper_path):
            print(f"❌ Privileged helper missing: {self.helper_path}")
            return False
        
        # Check file permissions and type
        stat_info = os.stat(self.helper_path)
        file_type = subprocess.run(['file', self.helper_path], capture_output=True, text=True)
        
        print(f"✅ Privileged helper exists: {self.helper_path}")
        print(f"   Permissions: {oct(stat_info.st_mode)[-3:]}")
        print(f"   Type: {file_type.stdout.strip()}")
        return True
    
    def search_for_helper(self) -> List[str]:
        """Search for the privileged helper in common locations."""
        print("\n🔍 Searching for privileged helper in common locations...")
        found_helpers = []
        
        search_paths = [
            "/Applications",
            "/System/Applications", 
            "/usr/local/bin",
            "/opt",
        ]
        
        # Also search in user home directories
        for user_home in Path("/Users").iterdir():
            if user_home.is_dir():
                search_paths.append(str(user_home))
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                print(f"   Searching in {search_path}...")
                try:
                    result = subprocess.run([
                        'find', search_path, 
                        '-name', '*opencore*', 
                        '-type', 'd'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line:
                                # Look for privileged helper in this directory
                                helper_search = subprocess.run([
                                    'find', line,
                                    '-name', '*privileged-helper*',
                                    '-type', 'f'
                                ], capture_output=True, text=True, timeout=10)
                                
                                if helper_search.returncode == 0:
                                    for helper in helper_search.stdout.strip().split('\n'):
                                        if helper:
                                            found_helpers.append(helper)
                                            print(f"     Found: {helper}")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        return found_helpers
    
    def list_existing_helpers(self) -> List[str]:
        """List existing privileged helper tools."""
        print("\n📋 Checking existing privileged helpers...")
        existing_helpers = []
        
        if os.path.exists(self.helper_dir):
            try:
                result = subprocess.run(['ls', '-la', self.helper_dir], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # More than just the header
                        print(f"   Found {len(lines) - 1} privileged helper(s):")
                        for line in lines[1:]:  # Skip header
                            if line.strip():
                                existing_helpers.append(line.strip())
                                print(f"     {line.strip()}")
                    else:
                        print("   No privileged helpers found")
                else:
                    print(f"   Error listing helpers: {result.stderr}")
            except Exception as e:
                print(f"   Error: {e}")
        
        return existing_helpers
    
    def suggest_solutions(self, found_helpers: List[str]) -> None:
        """Suggest solutions based on findings."""
        print("\n💡 Suggested Solutions:")
        print("=" * 50)
        
        if found_helpers:
            print("1. Copy the found privileged helper to the correct location:")
            for helper in found_helpers:
                print(f"   sudo cp '{helper}' {self.helper_path}")
                print(f"   sudo chmod +x {self.helper_path}")
            print()
        
        print("2. Reinstall OpenCore Legacy Patcher:")
        print("   - Download the latest version from the official repository")
        print("   - Ensure the installation process completes successfully")
        print("   - Check if the privileged helper is included in the installer")
        print()
        
        print("3. Manual installation:")
        print("   - Check the OpenCore Legacy Patcher application bundle")
        print("   - Look for a Resources or Support folder containing the helper")
        print("   - Copy the helper to the correct location")
        print()
        
        print("4. Check OpenCore Legacy Patcher documentation:")
        print("   - Visit: https://github.com/dortania/OpenCore-Legacy-Patcher")
        print("   - Look for installation instructions")
        print("   - Check for known issues with privileged helper installation")
        print()
        
        print("5. Verify system requirements:")
        print("   - Ensure you're running a supported macOS version")
        print("   - Check if System Integrity Protection (SIP) is properly configured")
        print("   - Verify that the OpenCore Legacy Patcher has necessary permissions")
    
    def run_diagnostic(self) -> None:
        """Run the complete diagnostic process."""
        print("OpenCore Legacy Patcher Privileged Helper Diagnostic")
        print("=" * 55)
        print()
        
        # Check root permissions
        if not self.check_root_permissions():
            return
        
        print()
        
        # Check helper directory
        self.check_helper_directory()
        
        # Check specific privileged helper
        helper_exists = self.check_privileged_helper()
        
        # List existing helpers
        existing_helpers = self.list_existing_helpers()
        
        # Search for helper in other locations
        found_helpers = self.search_for_helper()
        
        # Provide solutions
        if not helper_exists:
            self.suggest_solutions(found_helpers)
        
        print("\n" + "=" * 55)
        print("Diagnostic complete!")


def main():
    """Main entry point."""
    diagnostic = PrivilegedHelperDiagnostic()
    diagnostic.run_diagnostic()


if __name__ == "__main__":
    main()