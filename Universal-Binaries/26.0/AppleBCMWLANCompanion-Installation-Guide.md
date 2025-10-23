# AppleBCMWLANCompanion for macOS 26 (Tahoe) Installation Guide

## Overview

This package provides smart injection of AppleBCMWLANCompanion for macOS 26 (Tahoe), enabling legacy Broadcom Wi-Fi cards to work without root patches.

## Supported Hardware

- **BCM43602** (Device ID: 0x14E4, 0x43BA)
  - BCM943602BAED
  - BCM943602CDP
  - BCM943602CS
  - DW1830

- **BCM4350** (Device ID: 0x14E4, 0x43A3)
  - BCM94350ZAE
  - DW1820A

## Installation Components

### 1. Kernel Extension
- **Location**: `System/Library/Extensions/AppleBCMWLANCompanion.kext`
- **Purpose**: Main driver for Broadcom Wi-Fi compatibility
- **Dependencies**: Requires Lilu.kext (minimum version 1.4.7)

### 2. WiFi Agent
- **Location**: `System/Library/CoreServices/WiFiAgent.app`
- **Purpose**: Updated WiFi management agent compatible with macOS 26
- **Version**: 26.0

### 3. Firmware Files
- **Location**: `usr/share/firmware/brcm/`
- **Files**:
  - `brcmfmac4350-pcie_7.35.180.119.bin` (BCM4350 firmware)
  - `brcmfmac43602-pcie_7.35.177.61.bin` (BCM43602 firmware)

## Installation Instructions

### Prerequisites
1. Ensure Lilu.kext is installed and working
2. Disable System Integrity Protection (SIP) temporarily
3. Boot from recovery mode or external drive for system modification

### Step 1: Install Kernel Extension
```bash
# Copy the kext to system extensions directory
sudo cp -R AppleBCMWLANCompanion.kext /System/Library/Extensions/

# Set proper permissions
sudo chown -R root:wheel /System/Library/Extensions/AppleBCMWLANCompanion.kext
sudo chmod -R 755 /System/Library/Extensions/AppleBCMWLANCompanion.kext

# Rebuild kext cache
sudo kextcache -i /
```

### Step 2: Install WiFi Agent
```bash
# Backup existing WiFiAgent (if present)
sudo mv /System/Library/CoreServices/WiFiAgent.app /System/Library/CoreServices/WiFiAgent.app.backup

# Install updated WiFiAgent
sudo cp -R WiFiAgent.app /System/Library/CoreServices/

# Set proper permissions
sudo chown -R root:wheel /System/Library/CoreServices/WiFiAgent.app
sudo chmod -R 755 /System/Library/CoreServices/WiFiAgent.app
```

### Step 3: Install Firmware Files
```bash
# Create firmware directory
sudo mkdir -p /usr/share/firmware/brcm

# Copy firmware files
sudo cp brcmfmac4350-pcie_7.35.180.119.bin /usr/share/firmware/brcm/
sudo cp brcmfmac43602-pcie_7.35.177.61.bin /usr/share/firmware/brcm/

# Set proper permissions
sudo chown root:wheel /usr/share/firmware/brcm/*
sudo chmod 644 /usr/share/firmware/brcm/*
```

## OpenCore Configuration

Add the following to your `config.plist`:

### Kernel Extensions
```xml
<key>Add</key>
<array>
    <dict>
        <key>BundlePath</key>
        <string>Lilu.kext</string>
        <key>Comment</key>
        <string>Lilu - Arbitrary kext and process patching</string>
        <key>Enabled</key>
        <true/>
        <key>ExecutablePath</key>
        <string>Contents/MacOS/Lilu</string>
        <key>MaxKernel</key>
        <string></string>
        <key>MinKernel</key>
        <string>12.0.0</string>
        <key>PlistPath</key>
        <string>Contents/Info.plist</string>
    </dict>
    <dict>
        <key>BundlePath</key>
        <string>AppleBCMWLANCompanion.kext</string>
        <key>Comment</key>
        <string>AppleBCMWLANCompanion - Broadcom Wi-Fi support for macOS 26</string>
        <key>Enabled</key>
        <true/>
        <key>ExecutablePath</key>
        <string>Contents/MacOS/AppleBCMWLANCompanion</string>
        <key>MaxKernel</key>
        <string></string>
        <key>MinKernel</key>
        <string>26.0.0</string>
        <key>PlistPath</key>
        <string>Contents/Info.plist</string>
    </dict>
</array>
```

### Device Properties (if needed)
```xml
<key>DeviceProperties</key>
<dict>
    <key>Add</key>
    <dict>
        <key>PciRoot(0x0)/Pci(0x1C,0x0)/Pci(0x0,0x0)</key>
        <dict>
            <key>compatible</key>
            <string>pci14e4,43ba</string>
            <key>device-id</key>
            <data>ukM=</data>
            <key>vendor-id</key>
            <data>5BQ=</data>
        </dict>
    </dict>
</dict>
```

## Boot Arguments

Under normal circumstances, no special boot arguments are required. However, for debugging:

- `bcmc-debug=1` - Enable debug logging
- `bcmc-verbose=1` - Enable verbose output
- `-liludbgall` - Enable Lilu debug output (if using Lilu)

## Troubleshooting

### Common Issues

1. **Kext not loading**
   - Check that Lilu.kext is loaded first
   - Verify SIP is disabled during installation
   - Rebuild kext cache after installation

2. **Wi-Fi not detected**
   - Verify your hardware is supported (check device IDs)
   - Ensure firmware files are in correct location
   - Check system logs for error messages

3. **System crashes**
   - Boot in safe mode and remove the kext
   - Check compatibility with other kexts
   - Verify all dependencies are met

### Log Locations
- System logs: `/var/log/system.log`
- Kernel logs: `dmesg | grep -i bcm`
- AppleBCMWLANCompanion logs: Look for "BCMC" entries in system logs

## Version Information

- **AppleBCMWLANCompanion**: v1.0.0
- **Target macOS**: 26.0 (Tahoe)
- **Minimum Lilu**: 1.4.7
- **Build Date**: $(date)

## Support and Resources

- Original Project: https://github.com/0xFireWolf/AppleBCMWLANCompanion
- Discussion: https://www.insanelymac.com/forum/topic/361710-broadcom-fullmac-wi-fi-support-on-macos-sonoma-sequoia-and-tahoe-without-root-patches/
- Issues: Report compatibility issues on the GitHub repository

## License

This integration is based on AppleBCMWLANCompanion by FireWolf, licensed under BSD-3-Clause.
Copyright (C) 2023-2025 FireWolf @ FireWolf Pl. All Rights Reserved.

## Disclaimer

This is beta software. Use at your own risk. Always have a backup and recovery plan before installation.