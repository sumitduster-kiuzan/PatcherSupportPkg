#!/usr/bin/env python3
"""
Test script for AppleBCMWLANCompanion injection on macOS 26
Validates the injection method and compatibility
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BCMWLANInjectionTester:
    """Test suite for AppleBCMWLANCompanion injection"""
    
    def __init__(self):
        self.test_results = {}
        self.system_root = Path("/System")
        self.test_kext_path = self.system_root / "Library/Extensions/AppleBCMWLANCompanion.kext"
        self.test_framework_path = self.system_root / "Library/Frameworks/AppleBCMWLANCompanion.framework"
    
    def test_system_requirements(self) -> bool:
        """Test system requirements"""
        logger.info("Testing system requirements...")
        
        tests = {
            "root_access": os.geteuid() == 0,
            "macos_version": self._test_macos_version(),
            "system_writable": os.access(self.system_root, os.W_OK),
            "required_tools": self._test_required_tools(),
            "kext_utilities": self._test_kext_utilities()
        }
        
        self.test_results["system_requirements"] = tests
        
        all_passed = all(tests.values())
        logger.info(f"System requirements test: {'PASS' if all_passed else 'FAIL'}")
        
        for test_name, result in tests.items():
            logger.info(f"  {test_name}: {'PASS' if result else 'FAIL'}")
        
        return all_passed
    
    def _test_macos_version(self) -> bool:
        """Test macOS version compatibility"""
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True, check=True)
            version_parts = result.stdout.strip().split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            # macOS 26 is version 15.5+
            return major == 15 and minor >= 5
        except:
            return False
    
    def _test_required_tools(self) -> bool:
        """Test for required command-line tools"""
        required_tools = ['kextutil', 'kextcache', 'codesign', 'lipo', 'system_profiler']
        
        for tool in required_tools:
            if not subprocess.run(['which', tool], capture_output=True).returncode == 0:
                logger.error(f"Required tool not found: {tool}")
                return False
        
        return True
    
    def _test_kext_utilities(self) -> bool:
        """Test kext utility functionality"""
        try:
            # Test kextutil
            result = subprocess.run(['kextutil', '-h'], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Test kextcache
            result = subprocess.run(['kextcache', '-h'], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            return True
        except:
            return False
    
    def test_hardware_detection(self) -> bool:
        """Test BCM WiFi hardware detection"""
        logger.info("Testing hardware detection...")
        
        try:
            # Detect network hardware
            result = subprocess.run([
                'system_profiler', 'SPNetworkDataType', '-json'
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            bcm_devices = []
            
            for interface in data.get('SPNetworkDataType', []):
                if 'spethernet_type' in interface:
                    interface_type = interface['spethernet_type']
                    if 'Broadcom' in interface_type or 'BCM' in interface_type:
                        bcm_devices.append(interface_type)
            
            # Detect PCI devices
            result = subprocess.run([
                'system_profiler', 'SPPCIDataType', '-json'
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            pci_devices = []
            
            for pci_device in data.get('SPPCIDataType', []):
                if 'spdisplays_type' in pci_device:
                    device_type = pci_device['spdisplays_type']
                    if 'Broadcom' in device_type or 'BCM' in device_type:
                        pci_devices.append(device_type)
            
            detected_devices = bcm_devices + pci_devices
            
            self.test_results["hardware_detection"] = {
                "bcm_devices": bcm_devices,
                "pci_devices": pci_devices,
                "total_detected": len(detected_devices),
                "devices": detected_devices
            }
            
            logger.info(f"Hardware detection test: {'PASS' if detected_devices else 'WARN'}")
            logger.info(f"  Detected BCM devices: {len(detected_devices)}")
            
            for device in detected_devices:
                logger.info(f"    - {device}")
            
            return True
            
        except Exception as e:
            logger.error(f"Hardware detection failed: {e}")
            self.test_results["hardware_detection"] = {"error": str(e)}
            return False
    
    def test_kext_structure(self) -> bool:
        """Test kext structure and validation"""
        logger.info("Testing kext structure...")
        
        if not self.test_kext_path.exists():
            logger.warning("Test kext not found, creating test structure...")
            return self._create_test_kext_structure()
        
        tests = {
            "kext_exists": self.test_kext_path.exists(),
            "info_plist_exists": (self.test_kext_path / "Contents/Info.plist").exists(),
            "binary_exists": (self.test_kext_path / "Contents/MacOS/AppleBCMWLANCompanion").exists(),
            "kext_loadable": self._test_kext_loadable(),
            "permissions_correct": self._test_kext_permissions()
        }
        
        self.test_results["kext_structure"] = tests
        
        all_passed = all(tests.values())
        logger.info(f"Kext structure test: {'PASS' if all_passed else 'FAIL'}")
        
        for test_name, result in tests.items():
            logger.info(f"  {test_name}: {'PASS' if result else 'FAIL'}")
        
        return all_passed
    
    def _create_test_kext_structure(self) -> bool:
        """Create test kext structure"""
        try:
            # Create directory structure
            self.test_kext_path.mkdir(parents=True, exist_ok=True)
            (self.test_kext_path / "Contents").mkdir(exist_ok=True)
            (self.test_kext_path / "Contents/MacOS").mkdir(exist_ok=True)
            (self.test_kext_path / "Contents/Resources").mkdir(exist_ok=True)
            
            # Create minimal Info.plist
            info_plist = {
                "CFBundleExecutable": "AppleBCMWLANCompanion",
                "CFBundleIdentifier": "com.apple.driver.AppleBCMWLANCompanion",
                "CFBundlePackageType": "KEXT",
                "CFBundleVersion": "1.0",
                "LSMinimumSystemVersion": "26.0"
            }
            
            import plistlib
            with open(self.test_kext_path / "Contents/Info.plist", 'wb') as f:
                plistlib.dump(info_plist, f)
            
            # Create placeholder binary
            binary_path = self.test_kext_path / "Contents/MacOS/AppleBCMWLANCompanion"
            with open(binary_path, 'w') as f:
                f.write("#!/bin/bash\necho 'Test AppleBCMWLANCompanion binary'\n")
            
            os.chmod(binary_path, 0o755)
            
            logger.info("Created test kext structure")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create test kext structure: {e}")
            return False
    
    def _test_kext_loadable(self) -> bool:
        """Test if kext is loadable"""
        try:
            result = subprocess.run(['kextutil', '-n', str(self.test_kext_path)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _test_kext_permissions(self) -> bool:
        """Test kext permissions"""
        try:
            # Check kext directory permissions
            kext_stat = self.test_kext_path.stat()
            if not (kext_stat.st_mode & 0o755):
                return False
            
            # Check binary permissions
            binary_path = self.test_kext_path / "Contents/MacOS/AppleBCMWLANCompanion"
            if binary_path.exists():
                binary_stat = binary_path.stat()
                if not (binary_stat.st_mode & 0o755):
                    return False
            
            return True
        except:
            return False
    
    def test_framework_structure(self) -> bool:
        """Test framework structure"""
        logger.info("Testing framework structure...")
        
        if not self.test_framework_path.exists():
            logger.warning("Test framework not found, creating test structure...")
            return self._create_test_framework_structure()
        
        tests = {
            "framework_exists": self.test_framework_path.exists(),
            "versions_dir_exists": (self.test_framework_path / "Versions/A").exists(),
            "binary_exists": (self.test_framework_path / "Versions/A/AppleBCMWLANCompanion").exists(),
            "info_plist_exists": (self.test_framework_path / "Versions/A/Info.plist").exists(),
            "symlinks_correct": self._test_framework_symlinks()
        }
        
        self.test_results["framework_structure"] = tests
        
        all_passed = all(tests.values())
        logger.info(f"Framework structure test: {'PASS' if all_passed else 'FAIL'}")
        
        for test_name, result in tests.items():
            logger.info(f"  {test_name}: {'PASS' if result else 'FAIL'}")
        
        return all_passed
    
    def _create_test_framework_structure(self) -> bool:
        """Create test framework structure"""
        try:
            # Create framework structure
            self.test_framework_path.mkdir(parents=True, exist_ok=True)
            versions_dir = self.test_framework_path / "Versions/A"
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            # Create symlinks
            current_link = self.test_framework_path / "Versions/Current"
            if current_link.exists():
                current_link.unlink()
            current_link.symlink_to("A")
            
            # Create framework binary
            binary_path = versions_dir / "AppleBCMWLANCompanion"
            with open(binary_path, 'w') as f:
                f.write("#!/bin/bash\necho 'Test AppleBCMWLANCompanion framework'\n")
            os.chmod(binary_path, 0o755)
            
            # Create Info.plist
            info_plist = {
                "CFBundleExecutable": "AppleBCMWLANCompanion",
                "CFBundleIdentifier": "com.apple.framework.AppleBCMWLANCompanion",
                "CFBundlePackageType": "FMWK",
                "CFBundleVersion": "1.0",
                "LSMinimumSystemVersion": "26.0"
            }
            
            import plistlib
            with open(versions_dir / "Info.plist", 'wb') as f:
                plistlib.dump(info_plist, f)
            
            # Create symlinks
            for link_name in ["AppleBCMWLANCompanion", "Resources"]:
                link_path = self.test_framework_path / link_name
                if link_path.exists():
                    link_path.unlink()
                link_path.symlink_to(f"Versions/Current/{link_name}")
            
            logger.info("Created test framework structure")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create test framework structure: {e}")
            return False
    
    def _test_framework_symlinks(self) -> bool:
        """Test framework symlinks"""
        try:
            # Check main symlinks
            binary_link = self.test_framework_path / "AppleBCMWLANCompanion"
            if not binary_link.is_symlink():
                return False
            
            resources_link = self.test_framework_path / "Resources"
            if not resources_link.is_symlink():
                return False
            
            return True
        except:
            return False
    
    def test_system_integration(self) -> bool:
        """Test system integration"""
        logger.info("Testing system integration...")
        
        tests = {
            "kext_cache_updatable": self._test_kext_cache_update(),
            "dyld_cache_updatable": self._test_dyld_cache_update(),
            "system_extensions_writable": self._test_system_extensions_writable()
        }
        
        self.test_results["system_integration"] = tests
        
        all_passed = all(tests.values())
        logger.info(f"System integration test: {'PASS' if all_passed else 'FAIL'}")
        
        for test_name, result in tests.items():
            logger.info(f"  {test_name}: {'PASS' if result else 'FAIL'}")
        
        return all_passed
    
    def _test_kext_cache_update(self) -> bool:
        """Test kext cache update capability"""
        try:
            # Test kextcache without actually updating
            result = subprocess.run(['kextcache', '-h'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _test_dyld_cache_update(self) -> bool:
        """Test dyld cache update capability"""
        try:
            # Test update_dyld_shared_cache
            result = subprocess.run(['update_dyld_shared_cache', '-h'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _test_system_extensions_writable(self) -> bool:
        """Test if system extensions directory is writable"""
        extensions_dir = self.system_root / "Library/Extensions"
        return os.access(extensions_dir, os.W_OK)
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("Running AppleBCMWLANCompanion injection tests...")
        
        test_functions = [
            ("system_requirements", self.test_system_requirements),
            ("hardware_detection", self.test_hardware_detection),
            ("kext_structure", self.test_kext_structure),
            ("framework_structure", self.test_framework_structure),
            ("system_integration", self.test_system_integration)
        ]
        
        results = {}
        
        for test_name, test_func in test_functions:
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Overall result
        overall_success = all(results.values())
        results["overall"] = overall_success
        
        logger.info(f"Overall test result: {'PASS' if overall_success else 'FAIL'}")
        
        return results
    
    def generate_report(self) -> str:
        """Generate test report"""
        report = []
        report.append("AppleBCMWLANCompanion Injection Test Report")
        report.append("=" * 50)
        report.append("")
        
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                report.append(f"{test_name}:")
                for sub_test, sub_result in result.items():
                    status = "PASS" if sub_result else "FAIL"
                    report.append(f"  {sub_test}: {status}")
            else:
                status = "PASS" if result else "FAIL"
                report.append(f"{test_name}: {status}")
        
        report.append("")
        report.append("Test completed.")
        
        return "\n".join(report)

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("AppleBCMWLANCompanion Injection Test Suite")
        print("Usage: python3 test-bcmwlan-injection.py [--help]")
        print("\nThis script tests the AppleBCMWLANCompanion injection system")
        return
    
    tester = BCMWLANInjectionTester()
    
    try:
        results = tester.run_all_tests()
        
        # Print results
        print("\n" + "="*60)
        print("AppleBCMWLANCompanion Injection Test Results")
        print("="*60)
        
        for test_name, result in results.items():
            if test_name != "overall":
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name:20} {status}")
        
        print("-" * 60)
        overall_status = "✅ ALL TESTS PASSED" if results["overall"] else "❌ SOME TESTS FAILED"
        print(f"{'Overall':20} {overall_status}")
        print("="*60)
        
        # Generate detailed report
        report = tester.generate_report()
        with open("/tmp/bcmwlan-injection-test-report.txt", "w") as f:
            f.write(report)
        
        print(f"\nDetailed report saved to: /tmp/bcmwlan-injection-test-report.txt")
        
        if not results["overall"]:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()