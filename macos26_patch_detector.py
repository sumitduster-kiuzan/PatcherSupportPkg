#!/usr/bin/env python3
"""
macOS 26 Patch Detector
Automatically detects macOS version and selects appropriate patches for AppleBCMWLANCompanion
"""

import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MacOSVersion:
    major: int
    minor: int
    patch: int
    build: str
    full_version: str

class MacOS26PatchDetector:
    def __init__(self):
        self.current_version = None
        self.supported_versions = []
        self.patch_database = {}
        
    def detect_macos_version(self) -> MacOSVersion:
        """Detect current macOS version with detailed information"""
        try:
            # Get product version
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True, check=True)
            version_string = result.stdout.strip()
            
            # Get build number
            result = subprocess.run(['sw_vers', '-buildVersion'], 
                                  capture_output=True, text=True, check=True)
            build_string = result.stdout.strip()
            
            # Parse version
            version_parts = version_string.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            patch = int(version_parts[2]) if len(version_parts) > 2 else 0
            
            self.current_version = MacOSVersion(
                major=major,
                minor=minor,
                patch=patch,
                build=build_string,
                full_version=version_string
            )
            
            return self.current_version
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to detect macOS version: {e}")
    
    def is_macos_26_compatible(self) -> bool:
        """Check if current macOS version is compatible with macOS 26 patches"""
        if not self.current_version:
            self.detect_macos_version()
        
        # macOS 26 would be version 26.x.x
        return self.current_version.major >= 26
    
    def detect_hardware_compatibility(self) -> Dict[str, bool]:
        """Detect hardware compatibility for AppleBCMWLANCompanion"""
        compatibility = {
            "broadcom_wifi": False,
            "intel_wifi": False,
            "apple_silicon": False,
            "intel_chipset": False
        }
        
        try:
            # Check for Broadcom WiFi
            result = subprocess.run(['system_profiler', 'SPAirPortDataType', '-json'], 
                                  capture_output=True, text=True, check=True)
            airport_data = json.loads(result.stdout)
            
            if 'SPAirPortDataType' in airport_data:
                for item in airport_data['SPAirPortDataType']:
                    if 'card_type' in item:
                        card_type = item['card_type'].lower()
                        if 'broadcom' in card_type or 'bcm' in card_type:
                            compatibility["broadcom_wifi"] = True
                        elif 'intel' in card_type:
                            compatibility["intel_wifi"] = True
            
            # Check for Apple Silicon
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True, check=True)
            if 'arm64' in result.stdout:
                compatibility["apple_silicon"] = True
            else:
                compatibility["intel_chipset"] = True
                
        except subprocess.CalledProcessError:
            pass  # Hardware detection failed, continue with defaults
        
        return compatibility
    
    def detect_kext_requirements(self) -> List[str]:
        """Detect required kexts for AppleBCMWLANCompanion injection"""
        required_kexts = [
            "com.apple.iokit.IO80211Family",
            "com.apple.iokit.IO80211FamilyV2", 
            "com.apple.driver.AppleAirPortBrcmNIC",
            "com.apple.driver.AppleBCMWLANCore",
            "com.apple.driver.AppleBCMWLANCoreMac"
        ]
        
        available_kexts = []
        
        for kext_id in required_kexts:
            try:
                result = subprocess.run(['kextstat', '-b', kext_id], 
                                      capture_output=True, text=True, check=True)
                if result.returncode == 0:
                    available_kexts.append(kext_id)
            except subprocess.CalledProcessError:
                pass  # Kext not loaded
        
        return available_kexts
    
    def detect_system_integrity_protection(self) -> Dict[str, bool]:
        """Detect System Integrity Protection status"""
        sip_status = {
            "enabled": True,
            "kext_signing_required": True,
            "system_files_protected": True
        }
        
        try:
            result = subprocess.run(['csrutil', 'status'], 
                                  capture_output=True, text=True, check=True)
            status_output = result.stdout.lower()
            
            if 'disabled' in status_output:
                sip_status["enabled"] = False
                sip_status["kext_signing_required"] = False
                sip_status["system_files_protected"] = False
            elif 'kext signing disabled' in status_output:
                sip_status["kext_signing_required"] = False
                
        except subprocess.CalledProcessError:
            pass  # Assume SIP is enabled by default
        
        return sip_status
    
    def select_patch_strategy(self) -> Dict[str, any]:
        """Select the best patch strategy based on system detection"""
        if not self.current_version:
            self.detect_macos_version()
        
        hardware = self.detect_hardware_compatibility()
        sip_status = self.detect_system_integrity_protection()
        available_kexts = self.detect_kext_requirements()
        
        strategy = {
            "method": "unknown",
            "requires_sip_disable": False,
            "requires_kext_signing": False,
            "compatible_hardware": False,
            "patch_level": "minimal",
            "injection_points": [],
            "warnings": []
        }
        
        # Determine if hardware is compatible
        if hardware["broadcom_wifi"] or hardware["intel_wifi"]:
            strategy["compatible_hardware"] = True
        
        # Select injection method based on SIP status
        if not sip_status["enabled"]:
            strategy["method"] = "direct_kext_load"
            strategy["requires_sip_disable"] = False
        elif not sip_status["kext_signing_required"]:
            strategy["method"] = "signed_kext_load"
            strategy["requires_kext_signing"] = True
        else:
            strategy["method"] = "skyline_plugin"
            strategy["requires_sip_disable"] = True
            strategy["warnings"].append("SIP must be disabled for kext injection")
        
        # Determine patch level based on macOS version
        if self.current_version.major >= 26:
            strategy["patch_level"] = "full"
            strategy["injection_points"] = [
                "System/Library/Extensions/AppleBCMWLANCompanion.kext",
                "System/Library/CoreServices/WiFiAgent.app",
                "System/Library/CoreServices/ControlCenter.app"
            ]
        else:
            strategy["patch_level"] = "compatibility"
            strategy["warnings"].append("macOS 26 patches on older system may cause instability")
        
        # Add warnings for missing kexts
        missing_kexts = set([
            "com.apple.iokit.IO80211Family",
            "com.apple.driver.AppleAirPortBrcmNIC"
        ]) - set(available_kexts)
        
        if missing_kexts:
            strategy["warnings"].append(f"Missing required kexts: {', '.join(missing_kexts)}")
        
        return strategy
    
    def generate_patch_config(self) -> Dict[str, any]:
        """Generate comprehensive patch configuration"""
        if not self.current_version:
            self.detect_macos_version()
        
        strategy = self.select_patch_strategy()
        hardware = self.detect_hardware_compatibility()
        
        config = {
            "system_info": {
                "macos_version": self.current_version.full_version,
                "build_number": self.current_version.build,
                "architecture": "arm64" if hardware["apple_silicon"] else "x86_64"
            },
            "hardware_compatibility": hardware,
            "patch_strategy": strategy,
            "apple_bcmwlan_companion": {
                "target_version": "26.0",
                "injection_method": strategy["method"],
                "kext_identifier": "com.apple.driver.AppleBCMWLANCompanion",
                "bundle_version": "1.0.0",
                "compatibility_requirements": {
                    "minimum_macos": "26.0",
                    "maximum_macos": "26.9",
                    "required_kexts": [
                        "com.apple.iokit.IO80211Family",
                        "com.apple.driver.AppleAirPortBrcmNIC"
                    ]
                }
            },
            "injection_instructions": self._generate_injection_instructions(strategy)
        }
        
        return config
    
    def _generate_injection_instructions(self, strategy: Dict[str, any]) -> List[str]:
        """Generate step-by-step injection instructions"""
        instructions = []
        
        if strategy["method"] == "direct_kext_load":
            instructions.extend([
                "1. Ensure SIP is disabled",
                "2. Copy AppleBCMWLANCompanion.kext to /System/Library/Extensions/",
                "3. Set proper permissions (root:wheel, 755)",
                "4. Load kext using: sudo kextload /System/Library/Extensions/AppleBCMWLANCompanion.kext",
                "5. Verify loading with: kextstat | grep AppleBCMWLANCompanion"
            ])
        elif strategy["method"] == "signed_kext_load":
            instructions.extend([
                "1. Sign the kext with a valid certificate",
                "2. Copy signed kext to /Library/Extensions/",
                "3. Set proper permissions (root:wheel, 755)",
                "4. Load kext using: sudo kextload /Library/Extensions/AppleBCMWLANCompanion.kext",
                "5. Verify loading with: kextstat | grep AppleBCMWLANCompanion"
            ])
        elif strategy["method"] == "skyline_plugin":
            instructions.extend([
                "1. Disable SIP temporarily",
                "2. Install SkyLight plugin for runtime injection",
                "3. Re-enable SIP",
                "4. Plugin will handle kext loading automatically",
                "5. Monitor injection via SkyLight logs"
            ])
        
        return instructions

def main():
    """Main entry point for patch detection"""
    print("macOS 26 AppleBCMWLANCompanion Patch Detector")
    print("=" * 50)
    
    detector = MacOS26PatchDetector()
    
    try:
        # Detect system information
        version = detector.detect_macos_version()
        print(f"macOS Version: {version.full_version} (Build {version.build})")
        
        # Check compatibility
        compatible = detector.is_macos_26_compatible()
        print(f"macOS 26 Compatible: {'Yes' if compatible else 'No'}")
        
        # Generate patch configuration
        config = detector.generate_patch_config()
        
        # Save configuration
        config_path = Path("/workspace/macos26_patch_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\nPatch configuration saved to: {config_path}")
        print(f"Recommended injection method: {config['patch_strategy']['method']}")
        
        if config['patch_strategy']['warnings']:
            print("\nWarnings:")
            for warning in config['patch_strategy']['warnings']:
                print(f"  - {warning}")
        
        print("\nInjection Instructions:")
        for instruction in config['injection_instructions']:
            print(f"  {instruction}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())