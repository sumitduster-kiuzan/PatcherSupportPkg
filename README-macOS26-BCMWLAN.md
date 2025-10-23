# macOS 26 AppleBCMWLANCompanion Smart Patcher

A comprehensive solution for enabling Broadcom WiFi support on macOS 26 through smart injection and patching of AppleBCMWLANCompanion components.

## Overview

This patching system provides intelligent injection capabilities for AppleBCMWLANCompanion to enable legacy Broadcom WiFi hardware support on macOS 26. The solution includes:

- **Smart Injection**: Automatic detection and injection of AppleBCMWLANCompanion kext
- **Binary Patching**: Advanced patching of system frameworks for BCM WiFi support
- **macOS 26 Compatibility**: Full support for macOS 26 (15.5+) with proper version detection
- **Safety Features**: Comprehensive backup and restore capabilities
- **Hardware Detection**: Automatic detection of supported BCM WiFi devices

## Supported Hardware

The patcher supports a wide range of Broadcom WiFi devices:

- BCM43224, BCM43225, BCM43227, BCM43228
- BCM4331, BCM4335, BCM4339
- BCM4352, BCM4353, BCM4356, BCM4358, BCM4359
- BCM4360, BCM43602, BCM4364, BCM4365, BCM4366
- BCM4371, BCM4377, BCM4378
- BCM4387, BCM4398

## Requirements

- macOS 26 (15.5+) or compatible system
- Root access (sudo)
- Supported Broadcom WiFi hardware
- Internet connection for downloading dependencies

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/0xFireWolf/AppleBCMWLANCompanion.git
   cd AppleBCMWLANCompanion
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x *.py
   ```

3. **Run the patcher**:
   ```bash
   sudo python3 macos26-bcmwlan-patcher.py
   ```

## Usage

### Basic Usage

```bash
# Run the complete patching process
sudo python3 macos26-bcmwlan-patcher.py

# Dry run (no changes made)
sudo python3 macos26-bcmwlan-patcher.py --dry-run

# Verbose output
sudo python3 macos26-bcmwlan-patcher.py --verbose
```

### Advanced Usage

```bash
# Patch a different system root (e.g., mounted volume)
sudo python3 macos26-bcmwlan-patcher.py --system-root /Volumes/MacOS

# Run individual components
sudo python3 inject-applebcmwlancompanion.py
sudo python3 bcmwlan-binary-patcher.py /System
```

## Components

### 1. Main Patcher (`macos26-bcmwlan-patcher.py`)

The main orchestration script that:
- Checks system prerequisites
- Detects BCM WiFi hardware
- Creates system backups
- Coordinates all patching operations
- Verifies patch success

### 2. Smart Injector (`inject-applebcmwlancompanion.py`)

Handles the injection of AppleBCMWLANCompanion kext:
- macOS version detection
- Kext structure creation
- System integration
- Cache updates

### 3. Binary Patcher (`bcmwlan-binary-patcher.py`)

Advanced binary patching capabilities:
- Mach-O binary patching
- Framework modification
- Device ID recognition
- System framework updates

## Safety Features

### Automatic Backup

The patcher automatically creates comprehensive backups:
- Original system components
- BCM WiFi related files
- System frameworks
- Backup manifest with metadata

### Restore Capability

A restore script is automatically created at `/tmp/macos26-bcmwlan-backup/restore_system.sh`:

```bash
# Restore original system state
sudo /tmp/macos26-bcmwlan-backup/restore_system.sh
```

### Dry Run Mode

Test the patching process without making changes:

```bash
sudo python3 macos26-bcmwlan-patcher.py --dry-run
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure you're running with `sudo`
   - Check system integrity protection (SIP) status

2. **Hardware Not Detected**
   - Verify BCM WiFi hardware is installed
   - Check device compatibility list

3. **Patch Verification Failed**
   - Check system logs: `/tmp/macos26-bcmwlan-patcher.log`
   - Verify kext loading: `kextstat | grep BCM`

### Debug Mode

Enable verbose logging for detailed information:

```bash
sudo python3 macos26-bcmwlan-patcher.py --verbose
```

### Manual Verification

Check if the patch was successful:

```bash
# Check kext status
kextstat | grep AppleBCMWLANCompanion

# Check framework
ls -la /System/Library/Frameworks/AppleBCMWLANCompanion.framework

# Check system logs
log show --predicate 'subsystem contains "AppleBCMWLANCompanion"' --last 1h
```

## Technical Details

### macOS 26 Compatibility

The patcher is specifically designed for macOS 26 with:
- Version detection (15.5+)
- SDK compatibility (macosx26.0.internal)
- Xcode 17.0 support
- Proper kext loading mechanisms

### Kext Structure

AppleBCMWLANCompanion kext includes:
- Proper Info.plist with macOS 26 compatibility
- IOKit personalities for BCM device matching
- Required library dependencies
- Correct bundle structure

### Framework Integration

System frameworks are patched to:
- Recognize BCM WiFi devices
- Support legacy hardware
- Maintain system stability
- Preserve existing functionality

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original AppleBCMWLANCompanion project by 0xFireWolf
- Inspired by OpenCore Legacy Patcher community
- Thanks to the macOS hacking community for research and development

## Disclaimer

This software is provided for educational and research purposes. Use at your own risk. The authors are not responsible for any damage to your system. Always create backups before patching.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review system logs for error details

---

**Note**: This patcher is specifically designed for macOS 26 and may not work on other versions. Always test in a safe environment before applying to production systems.