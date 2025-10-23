# AppleBCMWLANCompanion for macOS 26 (Tahoe)

## Smart Injection Package for PatcherSupportPkg

This directory contains a complete integration of **AppleBCMWLANCompanion** for macOS 26 (Tahoe), providing legacy Broadcom Wi-Fi support without requiring root system patches.

## 🎯 What This Package Provides

### ✅ Complete Wi-Fi Solution
- **Kernel Extension**: AppleBCMWLANCompanion.kext v1.0.0
- **System Integration**: Updated WiFiAgent for macOS 26
- **Firmware Support**: BCM4350 and BCM43602 firmware files
- **Smart Installation**: Automated installation scripts
- **OpenCore Config**: Ready-to-use configuration templates

### ✅ Supported Hardware
| Chip | Device ID | Compatible Cards |
|------|-----------|------------------|
| BCM43602 | 0x14E4:0x43BA | DW1830, BCM943602BAED, BCM943602CDP, BCM943602CS |
| BCM4350 | 0x14E4:0x43A3 | DW1820A, BCM94350ZAE |

### ✅ macOS Compatibility
- **Primary Target**: macOS 26.0 (Tahoe) - Build 25A354
- **Backward Compatible**: Should work on macOS 15.x (Sequoia) and 14.x (Sonoma)
- **Dependencies**: Requires Lilu.kext 1.4.7+

## 🚀 Quick Start

### 1. Hardware Detection
```bash
sudo ./detect-broadcom-wifi.sh
```

### 2. Automated Installation
```bash
sudo ./install-bcmwlan-companion.sh
```

### 3. OpenCore Configuration
- Copy `OpenCore-Config-Template.plist` sections to your `config.plist`
- Place `AppleBCMWLANCompanion.kext` in your `EFI/OC/Kexts/` folder
- Ensure `Lilu.kext` is loaded before AppleBCMWLANCompanion

## 📁 Package Contents

```
26.0/
├── System/
│   └── Library/
│       ├── Extensions/
│       │   └── AppleBCMWLANCompanion.kext/     # Main driver
│       └── CoreServices/
│           └── WiFiAgent.app/                  # Updated WiFi agent
├── usr/
│   └── share/
│       └── firmware/
│           └── brcm/                           # Firmware files
│               ├── brcmfmac4350-pcie_7.35.180.119.bin
│               └── brcmfmac43602-pcie_7.35.177.61.bin
├── install-bcmwlan-companion.sh               # Smart installer
├── detect-broadcom-wifi.sh                    # Hardware detection
├── OpenCore-Config-Template.plist             # OpenCore template
├── AppleBCMWLANCompanion-Installation-Guide.md # Detailed guide
└── README.md                                   # This file
```

## 🔧 Manual Installation

### Prerequisites
1. **Disable SIP**: `csrutil disable` in Recovery Mode
2. **Install Lilu**: Ensure Lilu.kext is installed and working
3. **Backup System**: Always backup before system modifications

### Step-by-Step Installation

#### 1. Install Kernel Extension
```bash
sudo cp -R System/Library/Extensions/AppleBCMWLANCompanion.kext /System/Library/Extensions/
sudo chown -R root:wheel /System/Library/Extensions/AppleBCMWLANCompanion.kext
sudo chmod -R 755 /System/Library/Extensions/AppleBCMWLANCompanion.kext
```

#### 2. Install WiFi Agent
```bash
sudo cp -R System/Library/CoreServices/WiFiAgent.app /System/Library/CoreServices/
sudo chown -R root:wheel /System/Library/CoreServices/WiFiAgent.app
sudo chmod -R 755 /System/Library/CoreServices/WiFiAgent.app
```

#### 3. Install Firmware
```bash
sudo mkdir -p /usr/share/firmware/brcm
sudo cp usr/share/firmware/brcm/* /usr/share/firmware/brcm/
sudo chown root:wheel /usr/share/firmware/brcm/*
sudo chmod 644 /usr/share/firmware/brcm/*
```

#### 4. Rebuild Kext Cache
```bash
sudo kextcache -i /
```

## ⚙️ OpenCore Configuration

### Kernel Extensions
Add to `Kernel` → `Add`:
```xml
<dict>
    <key>BundlePath</key>
    <string>AppleBCMWLANCompanion.kext</string>
    <key>Enabled</key>
    <true/>
    <key>ExecutablePath</key>
    <string>Contents/MacOS/AppleBCMWLANCompanion</string>
    <key>MinKernel</key>
    <string>26.0.0</string>
    <key>PlistPath</key>
    <string>Contents/Info.plist</string>
</dict>
```

### Device Properties
Add to `DeviceProperties` → `Add` (replace PCI path with your device):
```xml
<key>PciRoot(0x0)/Pci(0x1C,0x0)/Pci(0x0,0x0)</key>
<dict>
    <key>compatible</key>
    <string>pci14e4,43ba</string>
    <key>device-id</key>
    <data>ukM=</data>
    <key>vendor-id</key>
    <data>5BQ=</data>
</dict>
```

## 🐛 Troubleshooting

### Common Issues

#### Kext Not Loading
- ✅ Verify Lilu.kext loads first
- ✅ Check SIP is disabled
- ✅ Rebuild kext cache: `sudo kextcache -i /`
- ✅ Check logs: `dmesg | grep -i bcm`

#### Wi-Fi Not Detected
- ✅ Verify hardware compatibility with detection script
- ✅ Check firmware files are in `/usr/share/firmware/brcm/`
- ✅ Verify device properties in OpenCore config
- ✅ Check system logs: `log show --predicate 'process == "kernel"' --info`

#### System Crashes
- ✅ Boot in safe mode and remove kext
- ✅ Check for conflicting kexts
- ✅ Verify all dependencies are met
- ✅ Use single-user mode for recovery

### Debug Options

#### Boot Arguments
- `bcmc-debug=1` - Enable debug logging
- `bcmc-verbose=1` - Enable verbose output
- `-liludbgall` - Enable Lilu debug output

#### Log Analysis
```bash
# System logs
sudo log show --predicate 'process == "kernel"' --info | grep -i bcm

# Kernel messages
dmesg | grep -i "bcm\|wifi\|wlan"

# AppleBCMWLANCompanion specific
sudo log show --predicate 'eventMessage contains "BCMC"' --info
```

## 📋 Version Information

- **AppleBCMWLANCompanion**: v1.0.0 (bef853e)
- **Target macOS**: 26.0 (Tahoe)
- **Minimum Lilu**: 1.4.7
- **Package Version**: 1.0.0
- **Build Date**: 2025-10-23

## 🔗 Resources

- **Original Project**: [AppleBCMWLANCompanion](https://github.com/0xFireWolf/AppleBCMWLANCompanion)
- **Discussion Forum**: [InsanelyMac Thread](https://www.insanelymac.com/forum/topic/361710-broadcom-fullmac-wi-fi-support-on-macos-sonoma-sequoia-and-tahoe-without-root-patches/)
- **PatcherSupportPkg**: [Main Repository](https://github.com/dortania/PatcherSupportPkg)
- **OpenCore Guide**: [Dortania's Guide](https://dortania.github.io/OpenCore-Install-Guide/)

## ⚠️ Important Notes

### Compatibility
- **Beta Software**: AppleBCMWLANCompanion is in beta - use at your own risk
- **System Requirements**: macOS 26.0+ with SIP disabled for installation
- **Hardware Specific**: Only works with BCM43602 and BCM4350 chips

### Support
- **Community Support**: Use InsanelyMac forum for community help
- **Bug Reports**: Report issues on the original GitHub repository
- **Documentation**: Refer to included installation guide for detailed help

### Legal
- **License**: BSD-3-Clause (AppleBCMWLANCompanion)
- **Copyright**: © 2023-2025 FireWolf @ FireWolf Pl.
- **Disclaimer**: Use at your own risk - always backup your system

## 🎉 Success Stories

After successful installation, you should see:
- ✅ Wi-Fi card detected in System Information
- ✅ Wi-Fi networks visible in menu bar
- ✅ Stable connection performance
- ✅ No kernel panics or system instability

---

**Happy Wi-Fi networking on macOS 26! 🚀**