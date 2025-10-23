#!/usr/bin/env python3
"""
macOS 26 AppleBCMWLANCompanion Smart Patcher
Comprehensive patching solution for Broadcom WiFi on macOS 26

This script provides a complete solution for injecting and patching
AppleBCMWLANCompanion to enable Broadcom WiFi support on macOS 26.
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# Import our custom modules
from inject_applebcmwlancompanion import AppleBCMWLANCompanionInjector
from bcmwlan_binary_patcher import BCMWLANBinaryPatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/macos26-bcmwlan-patcher.log')
    ]
)
logger = logging.getLogger(__name__)

class macOS26BCMWLANPatcher:
    """Main patcher class for macOS 26 BCM WiFi support"""
    
    def __init__(self, system_root: str = "/System", dry_run: bool = False):
        self.system_root = Path(system_root)
        self.dry_run = dry_run
        self.backup_dir = Path("/tmp/macos26-bcmwlan-backup")
        
        # Initialize components
        self.injector = AppleBCMWLANCompanionInjector(str(self.system_root))
        self.binary_patcher = BCMWLANBinaryPatcher()
        
        # macOS 26 specific configuration
        self.macos_26_config = {
            "version": "26.0",
            "build": "23A344014",
            "sdk": "macosx26.0.internal",
            "xcode": "1700",
            "xcode_build": "17A6231r"
        }
        
        # BCM WiFi device support
        self.supported_devices = [
            "BCM43224", "BCM43225", "BCM43227", "BCM43228",
            "BCM4331", "BCM4335", "BCM4339", "BCM4352",
            "BCM4353", "BCM4356", "BCM4358", "BCM4359",
            "BCM4360", "BCM43602", "BCM4364", "BCM4365",
            "BCM4366", "BCM4371", "BCM4377", "BCM4378",
            "BCM4387", "BCM4398"
        ]
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites for patching"""
        logger.info("Checking prerequisites...")
        
        # Check if running as root
        if os.geteuid() != 0:
            logger.error("This script must be run as root (use sudo)")
            return False
        
        # Check macOS version
        major, minor = self.injector.detect_macos_version()
        if major != 15 or minor < 5:
            logger.error(f"macOS 26 (15.5+) required, found {major}.{minor}")
            return False
        
        # Check if system is writable
        if not os.access(self.system_root, os.W_OK):
            logger.error(f"System root {self.system_root} is not writable")
            return False
        
        # Check for required tools
        required_tools = ['kextutil', 'kextcache', 'codesign', 'lipo']
        for tool in required_tools:
            if not shutil.which(tool):
                logger.error(f"Required tool not found: {tool}")
                return False
        
        logger.info("Prerequisites check passed")
        return True
    
    def detect_bcmwlan_hardware(self) -> List[str]:
        """Detect BCM WiFi hardware in the system"""
        logger.info("Detecting BCM WiFi hardware...")
        
        detected_devices = []
        
        try:
            # Use system_profiler to detect network hardware
            result = subprocess.run([
                'system_profiler', 'SPNetworkDataType', '-json'
            ], capture_output=True, text=True, check=True)
            
            # Parse JSON output to find BCM devices
            import json
            data = json.loads(result.stdout)
            
            for interface in data.get('SPNetworkDataType', []):
                if 'spethernet_type' in interface:
                    interface_type = interface['spethernet_type']
                    if 'Broadcom' in interface_type or 'BCM' in interface_type:
                        detected_devices.append(interface_type)
            
            # Also check PCI devices
            result = subprocess.run([
                'system_profiler', 'SPPCIDataType', '-json'
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            for pci_device in data.get('SPPCIDataType', []):
                if 'spdisplays_type' in pci_device:
                    device_type = pci_device['spdisplays_type']
                    if any(device in device_type for device in self.supported_devices):
                        detected_devices.append(device_type)
        
        except Exception as e:
            logger.warning(f"Hardware detection failed: {e}")
        
        if detected_devices:
            logger.info(f"Detected BCM devices: {', '.join(detected_devices)}")
        else:
            logger.warning("No BCM WiFi devices detected")
        
        return detected_devices
    
    def create_system_backup(self) -> bool:
        """Create comprehensive system backup"""
        logger.info("Creating system backup...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup existing BCM components
            bcm_components = [
                "Library/Extensions/AppleBCMWLANCompanion.kext",
                "Library/Frameworks/AppleBCMWLANCompanion.framework",
                "System/Library/Extensions/IO80211Family.kext",
                "System/Library/Frameworks/CoreWLAN.framework",
                "System/Library/PrivateFrameworks/CoreWiFi.framework"
            ]
            
            for component in bcm_components:
                source_path = self.system_root / component
                if source_path.exists():
                    backup_path = self.backup_dir / component
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_dir():
                        shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, backup_path)
                    
                    logger.info(f"Backed up: {component}")
            
            # Create backup manifest
            manifest = {
                "backup_date": str(Path().cwd()),
                "macos_version": self.injector.detect_macos_version(),
                "backed_up_components": bcm_components,
                "backup_location": str(self.backup_dir)
            }
            
            import json
            with open(self.backup_dir / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"System backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create system backup: {e}")
            return False
    
    def patch_system_frameworks(self) -> bool:
        """Patch system frameworks for BCM support"""
        logger.info("Patching system frameworks...")
        
        if self.dry_run:
            logger.info("DRY RUN: Would patch system frameworks")
            return True
        
        try:
            return self.binary_patcher.patch_system_frameworks(self.system_root)
        except Exception as e:
            logger.error(f"Failed to patch system frameworks: {e}")
            return False
    
    def inject_bcmwlan_kext(self) -> bool:
        """Inject AppleBCMWLANCompanion kext"""
        logger.info("Injecting AppleBCMWLANCompanion kext...")
        
        if self.dry_run:
            logger.info("DRY RUN: Would inject AppleBCMWLANCompanion kext")
            return True
        
        try:
            return self.injector.smart_inject()
        except Exception as e:
            logger.error(f"Failed to inject BCMWLAN kext: {e}")
            return False
    
    def update_system_caches(self) -> bool:
        """Update system caches after patching"""
        logger.info("Updating system caches...")
        
        if self.dry_run:
            logger.info("DRY RUN: Would update system caches")
            return True
        
        try:
            # Update kext cache
            subprocess.run(['kextcache', '-i', '/'], check=True)
            
            # Update dyld cache
            subprocess.run(['update_dyld_shared_cache', '-force'], check=True)
            
            # Touch system extensions directory
            extensions_dir = self.system_root / "Library/Extensions"
            if extensions_dir.exists():
                subprocess.run(['touch', str(extensions_dir)], check=True)
            
            logger.info("System caches updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update system caches: {e}")
            return False
    
    def verify_patch_success(self) -> bool:
        """Verify that patching was successful"""
        logger.info("Verifying patch success...")
        
        try:
            # Check if kext is loadable
            kext_path = self.system_root / "Library/Extensions/AppleBCMWLANCompanion.kext"
            if not kext_path.exists():
                logger.error("AppleBCMWLANCompanion kext not found")
                return False
            
            result = subprocess.run(['kextutil', '-n', str(kext_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Kext validation failed: {result.stderr}")
                return False
            
            # Check framework
            framework_path = self.system_root / "Library/Frameworks/AppleBCMWLANCompanion.framework"
            if not framework_path.exists():
                logger.warning("AppleBCMWLANCompanion framework not found")
            
            logger.info("Patch verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Patch verification failed: {e}")
            return False
    
    def create_restore_script(self) -> bool:
        """Create script to restore original system state"""
        logger.info("Creating restore script...")
        
        try:
            restore_script = self.backup_dir / "restore_system.sh"
            
            with open(restore_script, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# macOS 26 BCM WiFi Patcher Restore Script\n")
                f.write("# Run this script to restore original system state\n\n")
                f.write("set -e\n\n")
                f.write("echo 'Restoring system from backup...'\n\n")
                
                # Remove patched components
                f.write("# Remove patched components\n")
                f.write("rm -rf /System/Library/Extensions/AppleBCMWLANCompanion.kext\n")
                f.write("rm -rf /System/Library/Frameworks/AppleBCMWLANCompanion.framework\n\n")
                
                # Restore from backup
                f.write("# Restore from backup\n")
                f.write(f"if [ -d '{self.backup_dir}' ]; then\n")
                f.write("    cp -r {}/Library/Extensions/* /System/Library/Extensions/ 2>/dev/null || true\n".format(self.backup_dir))
                f.write("    cp -r {}/Library/Frameworks/* /System/Library/Frameworks/ 2>/dev/null || true\n".format(self.backup_dir))
                f.write("    cp -r {}/System/Library/Extensions/* /System/Library/Extensions/ 2>/dev/null || true\n".format(self.backup_dir))
                f.write("    cp -r {}/System/Library/Frameworks/* /System/Library/Frameworks/ 2>/dev/null || true\n".format(self.backup_dir))
                f.write("    cp -r {}/System/Library/PrivateFrameworks/* /System/Library/PrivateFrameworks/ 2>/dev/null || true\n".format(self.backup_dir))
                f.write("fi\n\n")
                
                # Update caches
                f.write("# Update system caches\n")
                f.write("kextcache -i /\n")
                f.write("update_dyld_shared_cache -force\n\n")
                
                f.write("echo 'System restore completed. Please reboot.'\n")
            
            os.chmod(restore_script, 0o755)
            logger.info(f"Restore script created: {restore_script}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create restore script: {e}")
            return False
    
    def run_complete_patch(self) -> bool:
        """Run the complete patching process"""
        logger.info("Starting macOS 26 BCM WiFi patching process")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Detect hardware
        detected_devices = self.detect_bcmwlan_hardware()
        if not detected_devices:
            logger.warning("No BCM WiFi devices detected, but continuing with patch...")
        
        # Create backup
        if not self.create_system_backup():
            logger.error("Failed to create system backup")
            return False
        
        # Patch system frameworks
        if not self.patch_system_frameworks():
            logger.error("Failed to patch system frameworks")
            return False
        
        # Inject BCMWLAN kext
        if not self.inject_bcmwlan_kext():
            logger.error("Failed to inject BCMWLAN kext")
            return False
        
        # Update system caches
        if not self.update_system_caches():
            logger.error("Failed to update system caches")
            return False
        
        # Verify patch success
        if not self.verify_patch_success():
            logger.error("Patch verification failed")
            return False
        
        # Create restore script
        if not self.create_restore_script():
            logger.warning("Failed to create restore script")
        
        logger.info("macOS 26 BCM WiFi patching completed successfully!")
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="macOS 26 AppleBCMWLANCompanion Smart Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 macos26-bcmwlan-patcher.py
  sudo python3 macos26-bcmwlan-patcher.py --dry-run
  sudo python3 macos26-bcmwlan-patcher.py --system-root /Volumes/MacOS
        """
    )
    
    parser.add_argument(
        '--system-root',
        default='/System',
        help='System root directory (default: /System)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without making changes'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    patcher = macOS26BCMWLANPatcher(
        system_root=args.system_root,
        dry_run=args.dry_run
    )
    
    try:
        if patcher.run_complete_patch():
            print("\n✅ macOS 26 BCM WiFi patching completed successfully!")
            print("🔄 Please reboot your system to activate the changes.")
            print(f"📁 Backup location: {patcher.backup_dir}")
            print(f"🔧 Restore script: {patcher.backup_dir}/restore_system.sh")
        else:
            print("\n❌ macOS 26 BCM WiFi patching failed!")
            print("📋 Check the logs for detailed error information.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Patching interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()