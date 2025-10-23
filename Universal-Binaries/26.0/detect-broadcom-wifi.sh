#!/bin/bash

# Broadcom Wi-Fi Hardware Detection Script
# For AppleBCMWLANCompanion compatibility checking

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo -e "${BLUE}Broadcom Wi-Fi Hardware Detection${NC}"
echo -e "${BLUE}AppleBCMWLANCompanion Compatibility Check${NC}"
echo "=========================================="
echo

# Function to convert hex device ID to description
get_device_description() {
    case "$1" in
        "43ba"|"0x43ba")
            echo "BCM43602 - Supported (DW1830, BCM943602BAED, BCM943602CDP, BCM943602CS)"
            return 0
            ;;
        "43a3"|"0x43a3")
            echo "BCM4350 - Supported (DW1820A, BCM94350ZAE)"
            return 0
            ;;
        "4331"|"0x4331")
            echo "BCM4331 - Not supported by AppleBCMWLANCompanion"
            return 1
            ;;
        "4360"|"0x4360")
            echo "BCM4360 - Not supported by AppleBCMWLANCompanion"
            return 1
            ;;
        "43a0"|"0x43a0")
            echo "BCM4360 (variant) - Not supported by AppleBCMWLANCompanion"
            return 1
            ;;
        *)
            echo "Unknown Broadcom device - Check compatibility manually"
            return 1
            ;;
    esac
}

# Check if system_profiler is available
if ! command -v system_profiler &> /dev/null; then
    echo -e "${RED}Error: system_profiler not found${NC}"
    echo "This script requires macOS system_profiler utility"
    exit 1
fi

echo -e "${CYAN}Scanning PCI devices for Broadcom Wi-Fi hardware...${NC}"
echo

# Get PCI device information
pci_data=$(system_profiler SPPCIDataType 2>/dev/null)

# Look for Broadcom devices (vendor ID 14e4)
broadcom_devices=$(echo "$pci_data" | grep -A 10 -B 5 "Vendor ID: 0x14e4" | grep -E "(Device ID|Vendor ID|BSD name|Location)" || true)

if [[ -z "$broadcom_devices" ]]; then
    echo -e "${YELLOW}No Broadcom PCI devices found${NC}"
    echo
else
    echo -e "${GREEN}Found Broadcom PCI devices:${NC}"
    echo "$broadcom_devices"
    echo
fi

# Look specifically for Wi-Fi related devices
wifi_devices=$(echo "$pci_data" | grep -i -A 15 -B 5 "network\|wifi\|wireless\|802\.11" | grep -E "14e4|broadcom" || true)

supported_count=0
unsupported_count=0

echo -e "${CYAN}Detailed Wi-Fi Device Analysis:${NC}"
echo

# Parse device IDs and check compatibility
device_ids=$(echo "$pci_data" | grep -A 1 "Vendor ID: 0x14e4" | grep "Device ID" | sed 's/.*Device ID: 0x//' | tr '[:upper:]' '[:lower:]')

if [[ -n "$device_ids" ]]; then
    while IFS= read -r device_id; do
        if [[ -n "$device_id" ]]; then
            description=$(get_device_description "$device_id")
            status=$?
            
            if [[ $status -eq 0 ]]; then
                echo -e "${GREEN}✓ Device ID: 0x$device_id - $description${NC}"
                ((supported_count++))
            else
                echo -e "${RED}✗ Device ID: 0x$device_id - $description${NC}"
                ((unsupported_count++))
            fi
        fi
    done <<< "$device_ids"
else
    echo -e "${YELLOW}No Broadcom devices with device IDs found${NC}"
fi

# Check for Wi-Fi interfaces
echo
echo -e "${CYAN}Network Interface Analysis:${NC}"
echo

# Get network interfaces
interfaces=$(networksetup -listallhardwareports 2>/dev/null | grep -A 1 "Wi-Fi\|AirPort" | grep "Device:" | sed 's/Device: //' || true)

if [[ -n "$interfaces" ]]; then
    echo -e "${GREEN}Wi-Fi interfaces found:${NC}"
    for interface in $interfaces; do
        echo "  - $interface"
        
        # Try to get more info about the interface
        if command -v ifconfig &> /dev/null; then
            mac_addr=$(ifconfig "$interface" 2>/dev/null | grep ether | awk '{print $2}' || true)
            if [[ -n "$mac_addr" ]]; then
                echo "    MAC Address: $mac_addr"
            fi
        fi
    done
else
    echo -e "${YELLOW}No Wi-Fi interfaces found${NC}"
fi

# Check for existing Broadcom kexts
echo
echo -e "${CYAN}Existing Broadcom Kext Analysis:${NC}"
echo

existing_kexts=$(find /System/Library/Extensions /Library/Extensions 2>/dev/null -name "*Broadcom*" -o -name "*BCM*" -o -name "*WLAN*" | grep -v AppleBCMWLANCompanion || true)

if [[ -n "$existing_kexts" ]]; then
    echo -e "${YELLOW}Existing Broadcom-related kexts found:${NC}"
    echo "$existing_kexts"
    echo
    echo -e "${YELLOW}Note: These may conflict with AppleBCMWLANCompanion${NC}"
else
    echo -e "${GREEN}No conflicting Broadcom kexts found${NC}"
fi

# Summary
echo
echo "=========================================="
echo -e "${BLUE}Compatibility Summary:${NC}"
echo "=========================================="

if [[ $supported_count -gt 0 ]]; then
    echo -e "${GREEN}✓ $supported_count supported Broadcom Wi-Fi device(s) found${NC}"
    echo -e "${GREEN}✓ AppleBCMWLANCompanion should work on this system${NC}"
    echo
    echo -e "${CYAN}Recommended next steps:${NC}"
    echo "1. Install AppleBCMWLANCompanion using the installation script"
    echo "2. Configure OpenCore with the provided template"
    echo "3. Reboot and test Wi-Fi functionality"
elif [[ $unsupported_count -gt 0 ]]; then
    echo -e "${RED}✗ Only unsupported Broadcom Wi-Fi devices found${NC}"
    echo -e "${RED}✗ AppleBCMWLANCompanion will not work on this system${NC}"
    echo
    echo -e "${CYAN}Alternative solutions:${NC}"
    echo "1. Use different Wi-Fi drivers for your hardware"
    echo "2. Consider upgrading to supported Wi-Fi card"
    echo "3. Use USB Wi-Fi adapter as alternative"
else
    echo -e "${YELLOW}? No Broadcom Wi-Fi devices detected${NC}"
    echo -e "${YELLOW}? Cannot determine AppleBCMWLANCompanion compatibility${NC}"
    echo
    echo -e "${CYAN}Possible reasons:${NC}"
    echo "1. No Broadcom Wi-Fi card installed"
    echo "2. Wi-Fi card not properly detected by system"
    echo "3. Wi-Fi card disabled in BIOS/UEFI"
fi

echo
echo "For more information, visit:"
echo "https://github.com/0xFireWolf/AppleBCMWLANCompanion"
echo