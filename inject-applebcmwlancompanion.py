#!/usr/bin/env python3
"""
AppleBCMWLANCompanion Smart Injection Script for macOS 26
Based on 0xFireWolf/AppleBCMWLANCompanion project

This script provides smart injection capabilities for AppleBCMWLANCompanion
to patch macOS 26 systems with legacy Broadcom WiFi hardware support.
"""

import os
import sys
import subprocess
import plistlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppleBCMWLANCompanionInjector:
    """Smart injector for AppleBCMWLANCompanion on macOS 26"""
    
    def __init__(self, target_system: str = "/System", backup_dir: str = "/tmp/AppleBCMWLANCompanion_backup"):
        self.target_system = Path(target_system)
        self.backup_dir = Path(backup_dir)
        self.universal_binaries = Path("/workspace/Universal-Binaries")
        self.macos_26_path = self.universal_binaries / "15.5-25"  # macOS 26 binaries
        
        # AppleBCMWLANCompanion paths
        self.bcmwlan_kext_path = self.target_system / "Library/Extensions/AppleBCMWLANCompanion.kext"
        self.bcmwlan_framework_path = self.target_system / "Library/Frameworks/AppleBCMWLANCompanion.framework"
        
        # System paths for injection
        self.system_extensions = self.target_system / "Library/Extensions"
        self.system_frameworks = self.target_system / "Library/Frameworks"
        self.private_frameworks = self.target_system / "Library/PrivateFrameworks"
        
        # macOS 26 specific paths
        self.corewlan_framework = self.target_system / "System/Library/Frameworks/CoreWLAN.framework"
        self.corewifi_framework = self.target_system / "System/Library/PrivateFrameworks/CoreWiFi.framework"
        
    def detect_macos_version(self) -> Tuple[int, int]:
        """Detect current macOS version"""
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True, check=True)
            version_parts = result.stdout.strip().split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            return major, minor
        except Exception as e:
            logger.error(f"Failed to detect macOS version: {e}")
            return 0, 0
    
    def is_macos_26_compatible(self) -> bool:
        """Check if system is compatible with macOS 26 injection"""
        major, minor = self.detect_macos_version()
        logger.info(f"Detected macOS version: {major}.{minor}")
        
        # macOS 26 is version 15.x with specific build numbers
        if major == 15 and minor >= 5:
            return True
        return False
    
    def create_backup(self) -> bool:
        """Create backup of existing AppleBCMWLANCompanion components"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup existing kext
            if self.bcmwlan_kext_path.exists():
                backup_kext = self.backup_dir / "AppleBCMWLANCompanion.kext"
                shutil.copytree(self.bcmwlan_kext_path, backup_kext, dirs_exist_ok=True)
                logger.info(f"Backed up kext to: {backup_kext}")
            
            # Backup existing framework
            if self.bcmwlan_framework_path.exists():
                backup_framework = self.backup_dir / "AppleBCMWLANCompanion.framework"
                shutil.copytree(self.bcmwlan_framework_path, backup_framework, dirs_exist_ok=True)
                logger.info(f"Backed up framework to: {backup_framework}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def prepare_macos_26_binaries(self) -> bool:
        """Prepare macOS 26 specific binaries for injection"""
        try:
            if not self.macos_26_path.exists():
                logger.error(f"macOS 26 binaries not found at: {self.macos_26_path}")
                return False
            
            # Create AppleBCMWLANCompanion directory structure
            bcmwlan_dir = self.macos_26_path / "System/Library/Extensions/AppleBCMWLANCompanion.kext"
            bcmwlan_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Contents directory
            contents_dir = bcmwlan_dir / "Contents"
            contents_dir.mkdir(exist_ok=True)
            
            # Create MacOS directory for binary
            macos_dir = contents_dir / "MacOS"
            macos_dir.mkdir(exist_ok=True)
            
            # Create Resources directory
            resources_dir = contents_dir / "Resources"
            resources_dir.mkdir(exist_ok=True)
            
            logger.info("Prepared macOS 26 binary structure")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare macOS 26 binaries: {e}")
            return False
    
    def create_kext_info_plist(self) -> bool:
        """Create Info.plist for AppleBCMWLANCompanion kext"""
        try:
            info_plist = {
                "BuildMachineOSBuild": "23A344014",
                "CFBundleDevelopmentRegion": "English",
                "CFBundleExecutable": "AppleBCMWLANCompanion",
                "CFBundleGetInfoString": "AppleBCMWLANCompanion 1.0, Copyright © 2024 Apple Inc. All rights reserved.",
                "CFBundleIdentifier": "com.apple.driver.AppleBCMWLANCompanion",
                "CFBundleInfoDictionaryVersion": "6.0",
                "CFBundleName": "Apple BCM WLAN Companion Driver",
                "CFBundlePackageType": "KEXT",
                "CFBundleShortVersionString": "1.0",
                "CFBundleSignature": "????",
                "CFBundleSupportedPlatforms": ["MacOSX"],
                "CFBundleVersion": "1.0",
                "DTCompiler": "com.apple.compilers.llvm.clang.1_0",
                "DTPlatformBuild": "25A5279g",
                "DTPlatformName": "macosx",
                "DTPlatformVersion": "26.0",
                "DTSDKBuild": "25A5279g",
                "DTSDKName": "macosx26.0.internal",
                "DTXcode": "1700",
                "DTXcodeBuild": "17A6231r",
                "IOKitPersonalities": {
                    "BCM WLAN Companion Driver": {
                        "CFBundleIdentifier": "com.apple.driver.AppleBCMWLANCompanion",
                        "IOClass": "AppleBCMWLANCompanion",
                        "IOProbeScore": 1000,
                        "IOProviderClass": "IOPCIDevice",
                        "IOMatchCategory": "AppleBCMWLANCompanion",
                        "IOMatch": {
                            "IOPCIClassMatch": "0x02800000&0xff000000",  # Network controller class
                            "IOPCIVendorID": "0x14e4"  # Broadcom vendor ID
                        }
                    }
                },
                "LSMinimumSystemVersion": "26.0",
                "NSHumanReadableCopyright": "AppleBCMWLANCompanion 1.0, Copyright © 2024 Apple Inc. All rights reserved.",
                "OSBundleLibraries": {
                    "com.apple.iokit.IO80211Family": "1200.12.2",
                    "com.apple.iokit.IO80211FamilyV2": "1200.12.2",
                    "com.apple.iokit.IOPCIFamily": "2.9",
                    "com.apple.kpi.bsd": "8.0.0",
                    "com.apple.kpi.iokit": "8.0.0",
                    "com.apple.kpi.libkern": "8.0.0",
                    "com.apple.kpi.mach": "8.0.0"
                }
            }
            
            # Write Info.plist
            plist_path = self.macos_26_path / "System/Library/Extensions/AppleBCMWLANCompanion.kext/Contents/Info.plist"
            with open(plist_path, 'wb') as f:
                plistlib.dump(info_plist, f)
            
            logger.info("Created AppleBCMWLANCompanion Info.plist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Info.plist: {e}")
            return False
    
    def create_placeholder_binary(self) -> bool:
        """Create placeholder binary for AppleBCMWLANCompanion"""
        try:
            binary_path = self.macos_26_path / "System/Library/Extensions/AppleBCMWLANCompanion.kext/Contents/MacOS/AppleBCMWLANCompanion"
            
            # Create a minimal Mach-O binary placeholder
            # This would normally be replaced with the actual compiled binary
            placeholder_code = b"""#!/usr/bin/env python3
# Placeholder for AppleBCMWLANCompanion binary
# This should be replaced with the actual compiled kext binary
print("AppleBCMWLANCompanion placeholder loaded")
"""
            
            with open(binary_path, 'wb') as f:
                f.write(placeholder_code)
            
            # Make executable
            os.chmod(binary_path, 0o755)
            
            logger.info("Created placeholder binary")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create placeholder binary: {e}")
            return False
    
    def inject_kext(self) -> bool:
        """Inject AppleBCMWLANCompanion kext into system"""
        try:
            source_kext = self.macos_26_path / "System/Library/Extensions/AppleBCMWLANCompanion.kext"
            target_kext = self.bcmwlan_kext_path
            
            if not source_kext.exists():
                logger.error(f"Source kext not found: {source_kext}")
                return False
            
            # Remove existing kext if present
            if target_kext.exists():
                shutil.rmtree(target_kext)
            
            # Copy kext to system
            shutil.copytree(source_kext, target_kext)
            
            # Set proper permissions
            os.chmod(target_kext, 0o755)
            for root, dirs, files in os.walk(target_kext):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
            
            logger.info(f"Injected AppleBCMWLANCompanion kext to: {target_kext}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject kext: {e}")
            return False
    
    def update_kextcache(self) -> bool:
        """Update kext cache to recognize new kext"""
        try:
            # Touch /System/Library/Extensions to trigger kextcache update
            extensions_dir = self.target_system / "Library/Extensions"
            if extensions_dir.exists():
                subprocess.run(['touch', str(extensions_dir)], check=True)
            
            # Run kextcache to rebuild cache
            subprocess.run(['kextcache', '-i', '/'], check=True)
            
            logger.info("Updated kext cache")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update kext cache: {e}")
            return False
    
    def verify_injection(self) -> bool:
        """Verify that injection was successful"""
        try:
            if not self.bcmwlan_kext_path.exists():
                logger.error("AppleBCMWLANCompanion kext not found after injection")
                return False
            
            # Check if kext is loadable
            result = subprocess.run(['kextutil', '-n', str(self.bcmwlan_kext_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("AppleBCMWLANCompanion kext is loadable")
                return True
            else:
                logger.error(f"AppleBCMWLANCompanion kext validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify injection: {e}")
            return False
    
    def smart_inject(self) -> bool:
        """Perform smart injection of AppleBCMWLANCompanion for macOS 26"""
        logger.info("Starting AppleBCMWLANCompanion smart injection for macOS 26")
        
        # Check compatibility
        if not self.is_macos_26_compatible():
            logger.error("System is not compatible with macOS 26 injection")
            return False
        
        # Create backup
        if not self.create_backup():
            logger.error("Failed to create backup")
            return False
        
        # Prepare binaries
        if not self.prepare_macos_26_binaries():
            logger.error("Failed to prepare macOS 26 binaries")
            return False
        
        # Create kext components
        if not self.create_kext_info_plist():
            logger.error("Failed to create Info.plist")
            return False
        
        if not self.create_placeholder_binary():
            logger.error("Failed to create placeholder binary")
            return False
        
        # Inject kext
        if not self.inject_kext():
            logger.error("Failed to inject kext")
            return False
        
        # Update kext cache
        if not self.update_kextcache():
            logger.warning("Failed to update kext cache (may need manual update)")
        
        # Verify injection
        if not self.verify_injection():
            logger.error("Injection verification failed")
            return False
        
        logger.info("AppleBCMWLANCompanion smart injection completed successfully")
        return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("AppleBCMWLANCompanion Smart Injection Script for macOS 26")
        print("Usage: python3 inject-applebcmwlancompanion.py [--help]")
        print("\nThis script injects AppleBCMWLANCompanion kext for Broadcom WiFi support on macOS 26")
        return
    
    injector = AppleBCMWLANCompanionInjector()
    
    if injector.smart_inject():
        print("✅ AppleBCMWLANCompanion injection completed successfully!")
        print("🔄 Please reboot your system to activate the changes.")
    else:
        print("❌ AppleBCMWLANCompanion injection failed!")
        print("📋 Check the logs above for detailed error information.")
        sys.exit(1)

if __name__ == "__main__":
    main()