# AppleBCMWLANCompanion Smart Injector for macOS 26

This repository contains smart injection tools for patching AppleBCMWLANCompanion into macOS 26, based on the [0xFireWolf/AppleBCMWLANCompanion](https://github.com/0xFireWolf/AppleBCMWLANCompanion) project.

## Overview

The AppleBCMWLANCompanion Smart Injector provides intelligent patching capabilities for macOS 26, allowing legacy Broadcom WiFi hardware to work with newer macOS versions through smart kext injection and runtime patching.

## Features

- **Smart Detection**: Automatically detects macOS version, hardware compatibility, and SIP status
- **Multiple Injection Methods**: Supports direct kext loading, signed kext loading, and SkyLight plugin injection
- **Hardware Compatibility**: Detects Broadcom and Intel WiFi hardware
- **SIP-Aware**: Works with or without System Integrity Protection
- **Comprehensive Logging**: Detailed injection reports and error handling

## Files

### Core Scripts

- `apple_bcmwlan_injector.py` - Main injection script for AppleBCMWLANCompanion
- `macos26_patch_detector.py` - System detection and patch strategy selection
- `README_AppleBCMWLANCompanion.md` - This documentation

### Generated Files

- `Universal-Binaries/26.0/` - macOS 26 patch directory structure
- `macos26_patch_config.json` - System-specific patch configuration
- `apple_bcmwlan_injection_report.txt` - Detailed injection report

## Quick Start

### 1. System Detection

First, run the patch detector to analyze your system:

```bash
python3 macos26_patch_detector.py
```

This will:
- Detect your macOS version
- Check hardware compatibility
- Analyze SIP status
- Generate a patch configuration
- Provide injection instructions

### 2. Injection

Run the main injector:

```bash
python3 apple_bcmwlan_injector.py
```

This will:
- Create the necessary directory structure
- Generate AppleBCMWLANCompanion kext
- Create injection scripts
- Set up SkyLight plugins
- Generate a detailed report

## Injection Methods

### Method 1: Direct Kext Loading (SIP Disabled)

**Requirements**: SIP disabled, root access

```bash
# Disable SIP
sudo csrutil disable

# Run injection
python3 apple_bcmwlan_injector.py

# Load the kext
sudo kextload /System/Library/Extensions/AppleBCMWLANCompanion.kext

# Re-enable SIP
sudo csrutil enable
```

### Method 2: Signed Kext Loading (SIP Enabled)

**Requirements**: Valid code signing certificate

```bash
# Sign the kext
codesign -f -s "Your Certificate" AppleBCMWLANCompanion.kext

# Install to /Library/Extensions
sudo cp -R AppleBCMWLANCompanion.kext /Library/Extensions/

# Load the kext
sudo kextload /Library/Extensions/AppleBCMWLANCompanion.kext
```

### Method 3: SkyLight Plugin Injection

**Requirements**: SkyLight plugin system

The injector automatically creates SkyLight plugins for runtime injection. This method works with SIP enabled and provides the most seamless experience.

## Hardware Compatibility

### Supported Hardware

- **Broadcom WiFi Cards**: BCM43xx, BCM4360, BCM4364, BCM4371, BCM4377, BCM4378, BCM4387
- **Intel WiFi Cards**: Various Intel WiFi 6/6E cards
- **Architectures**: Intel x86_64 and Apple Silicon (ARM64)

### Detection

The system automatically detects:
- WiFi card manufacturer and model
- System architecture
- Required kexts
- SIP status
- Available injection methods

## Directory Structure

```
Universal-Binaries/
├── 26.0/                          # macOS 26 patches
│   └── System/
│       └── Library/
│           └── Extensions/
│               └── AppleBCMWLANCompanion.kext/
│                   ├── Contents/
│                   │   ├── Info.plist
│                   │   ├── MacOS/
│                   │   │   └── AppleBCMWLANCompanion
│                   │   └── Resources/
│                   │       ├── inject.sh
│                   │       └── patch_config.json
└── SkyLightPlugins/
    └── Library/
        └── Application Support/
            └── SkyLightPlugins/
                ├── AppleBCMWLANCompanion.dylib
                └── AppleBCMWLANCompanion.txt
```

## Configuration

### Patch Configuration

The system generates a `macos26_patch_config.json` file with:

```json
{
  "system_info": {
    "macos_version": "26.0",
    "build_number": "26A1234",
    "architecture": "arm64"
  },
  "hardware_compatibility": {
    "broadcom_wifi": true,
    "intel_wifi": false,
    "apple_silicon": true,
    "intel_chipset": false
  },
  "patch_strategy": {
    "method": "skyline_plugin",
    "requires_sip_disable": false,
    "compatible_hardware": true,
    "patch_level": "full"
  }
}
```

### Kext Info.plist

The generated kext includes proper IOKit personalities:

```xml
<key>IOKitPersonalities</key>
<dict>
    <key>AppleBCMWLANCompanion</key>
    <dict>
        <key>CFBundleIdentifier</key>
        <string>com.apple.driver.AppleBCMWLANCompanion</string>
        <key>IOClass</key>
        <string>AppleBCMWLANCompanion</string>
        <key>IOMatchCategory</key>
        <string>IODriver</string>
        <key>IOPCIPrimaryMatch</key>
        <string>0x43e0 0x14e4 0x43e1 0x14e4 0x43e2 0x14e4 0x43e3 0x14e4</string>
        <key>IOProviderClass</key>
        <string>IOPCIDevice</string>
    </dict>
</dict>
```

## Troubleshooting

### Common Issues

1. **SIP Enabled**: Use signed kext loading or SkyLight plugin method
2. **Hardware Not Detected**: Check if your WiFi card is supported
3. **Kext Won't Load**: Verify permissions and signing
4. **System Instability**: Ensure you're using the correct patch level

### Debugging

1. Check the injection report: `cat apple_bcmwlan_injection_report.txt`
2. Verify kext loading: `kextstat | grep AppleBCMWLANCompanion`
3. Check system logs: `log show --predicate 'subsystem == "com.apple.iokit.IO80211Family"'`

### Logs

The injector provides detailed logging:
- System detection results
- Hardware compatibility status
- Injection method selection
- File creation and permissions
- Error messages and warnings

## Security Considerations

- **SIP Disable**: Only disable SIP temporarily during injection
- **Code Signing**: Use proper certificates for production use
- **System Integrity**: Always re-enable SIP after injection
- **Backup**: Create system backups before patching

## Contributing

This project extends the PatcherSupportPkg repository. Contributions should:

1. Follow the existing code structure
2. Include proper error handling
3. Add comprehensive logging
4. Test on multiple hardware configurations
5. Update documentation

## License

This project follows the same license as the parent PatcherSupportPkg repository.

## Acknowledgments

- [0xFireWolf](https://github.com/0xFireWolf) for the original AppleBCMWLANCompanion project
- [Dortania](https://dortania.github.io/) for OpenCore Legacy Patcher
- The macOS patching community for continued development

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the injection report
3. Verify hardware compatibility
4. Check system requirements

---

**Warning**: This tool modifies system files and kexts. Use at your own risk and always create backups before proceeding.