#!/bin/bash

# AppleBCMWLANCompanion Smart Installation Script for macOS 26
# Copyright (C) 2025 - Smart injection for PatcherSupportPkg
# Based on AppleBCMWLANCompanion by 0xFireWolf

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEXT_NAME="AppleBCMWLANCompanion.kext"
WIFI_AGENT="WiFiAgent.app"
FIRMWARE_DIR="/usr/share/firmware/brcm"
EXTENSIONS_DIR="/System/Library/Extensions"
CORESERVICES_DIR="/System/Library/CoreServices"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check macOS version
check_macos_version() {
    local version=$(sw_vers -productVersion)
    local major=$(echo $version | cut -d. -f1)
    
    log "Detected macOS version: $version"
    
    if [[ $major -lt 26 ]]; then
        warning "This package is designed for macOS 26 (Tahoe). Current version: $version"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check SIP status
check_sip() {
    local sip_status=$(csrutil status 2>/dev/null || echo "unknown")
    
    if [[ $sip_status == *"enabled"* ]]; then
        error "System Integrity Protection (SIP) is enabled"
        error "Please disable SIP in Recovery Mode before running this script"
        error "Run 'csrutil disable' in Recovery Terminal"
        exit 1
    fi
    
    log "SIP status: $sip_status"
}

# Check for Lilu.kext
check_lilu() {
    if [[ ! -d "$EXTENSIONS_DIR/Lilu.kext" ]]; then
        warning "Lilu.kext not found in $EXTENSIONS_DIR"
        warning "AppleBCMWLANCompanion requires Lilu.kext to function"
        read -p "Continue without Lilu? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        success "Lilu.kext found"
    fi
}

# Detect Broadcom Wi-Fi hardware
detect_hardware() {
    log "Scanning for supported Broadcom Wi-Fi hardware..."
    
    local bcm_devices=$(system_profiler SPPCIDataType | grep -i "14e4\|broadcom" | grep -E "43ba|43a3" || true)
    
    if [[ -n "$bcm_devices" ]]; then
        success "Supported Broadcom Wi-Fi hardware detected:"
        echo "$bcm_devices"
    else
        warning "No supported Broadcom Wi-Fi hardware detected"
        warning "Supported devices: BCM43602 (43ba), BCM4350 (43a3)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Backup existing files
backup_existing() {
    local backup_dir="/System/Library/Backups/AppleBCMWLANCompanion-$(date +%Y%m%d-%H%M%S)"
    
    log "Creating backup directory: $backup_dir"
    mkdir -p "$backup_dir"
    
    # Backup existing kext if present
    if [[ -d "$EXTENSIONS_DIR/$KEXT_NAME" ]]; then
        log "Backing up existing $KEXT_NAME"
        cp -R "$EXTENSIONS_DIR/$KEXT_NAME" "$backup_dir/"
    fi
    
    # Backup existing WiFiAgent if present
    if [[ -d "$CORESERVICES_DIR/$WIFI_AGENT" ]]; then
        log "Backing up existing $WIFI_AGENT"
        cp -R "$CORESERVICES_DIR/$WIFI_AGENT" "$backup_dir/"
    fi
    
    success "Backup completed: $backup_dir"
}

# Install kernel extension
install_kext() {
    log "Installing AppleBCMWLANCompanion.kext..."
    
    if [[ ! -d "$SCRIPT_DIR/System/Library/Extensions/$KEXT_NAME" ]]; then
        error "AppleBCMWLANCompanion.kext not found in package"
        exit 1
    fi
    
    # Remove existing kext
    if [[ -d "$EXTENSIONS_DIR/$KEXT_NAME" ]]; then
        log "Removing existing $KEXT_NAME"
        rm -rf "$EXTENSIONS_DIR/$KEXT_NAME"
    fi
    
    # Copy new kext
    cp -R "$SCRIPT_DIR/System/Library/Extensions/$KEXT_NAME" "$EXTENSIONS_DIR/"
    
    # Set permissions
    chown -R root:wheel "$EXTENSIONS_DIR/$KEXT_NAME"
    chmod -R 755 "$EXTENSIONS_DIR/$KEXT_NAME"
    
    success "AppleBCMWLANCompanion.kext installed"
}

# Install WiFi Agent
install_wifi_agent() {
    log "Installing updated WiFiAgent..."
    
    if [[ ! -d "$SCRIPT_DIR/System/Library/CoreServices/$WIFI_AGENT" ]]; then
        error "WiFiAgent.app not found in package"
        exit 1
    fi
    
    # Remove existing WiFiAgent
    if [[ -d "$CORESERVICES_DIR/$WIFI_AGENT" ]]; then
        log "Removing existing $WIFI_AGENT"
        rm -rf "$CORESERVICES_DIR/$WIFI_AGENT"
    fi
    
    # Copy new WiFiAgent
    cp -R "$SCRIPT_DIR/System/Library/CoreServices/$WIFI_AGENT" "$CORESERVICES_DIR/"
    
    # Set permissions
    chown -R root:wheel "$CORESERVICES_DIR/$WIFI_AGENT"
    chmod -R 755 "$CORESERVICES_DIR/$WIFI_AGENT"
    
    success "WiFiAgent installed"
}

# Install firmware files
install_firmware() {
    log "Installing Broadcom firmware files..."
    
    # Create firmware directory
    mkdir -p "$FIRMWARE_DIR"
    
    # Copy firmware files
    if [[ -f "$SCRIPT_DIR/usr/share/firmware/brcm/brcmfmac4350-pcie_7.35.180.119.bin" ]]; then
        cp "$SCRIPT_DIR/usr/share/firmware/brcm/brcmfmac4350-pcie_7.35.180.119.bin" "$FIRMWARE_DIR/"
        success "BCM4350 firmware installed"
    else
        warning "BCM4350 firmware not found in package"
    fi
    
    if [[ -f "$SCRIPT_DIR/usr/share/firmware/brcm/brcmfmac43602-pcie_7.35.177.61.bin" ]]; then
        cp "$SCRIPT_DIR/usr/share/firmware/brcm/brcmfmac43602-pcie_7.35.177.61.bin" "$FIRMWARE_DIR/"
        success "BCM43602 firmware installed"
    else
        warning "BCM43602 firmware not found in package"
    fi
    
    # Set permissions
    chown root:wheel "$FIRMWARE_DIR"/*
    chmod 644 "$FIRMWARE_DIR"/*
}

# Rebuild kext cache
rebuild_cache() {
    log "Rebuilding kernel extension cache..."
    
    # Touch Extensions directory to trigger cache rebuild
    touch "$EXTENSIONS_DIR"
    
    # Rebuild kext cache
    if command -v kextcache >/dev/null 2>&1; then
        kextcache -i / || {
            warning "Failed to rebuild kext cache automatically"
            warning "You may need to rebuild manually after reboot"
        }
        success "Kernel extension cache rebuilt"
    else
        warning "kextcache command not available"
        warning "Cache will be rebuilt on next boot"
    fi
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    local errors=0
    
    # Check kext
    if [[ -d "$EXTENSIONS_DIR/$KEXT_NAME" ]]; then
        success "✓ AppleBCMWLANCompanion.kext installed"
    else
        error "✗ AppleBCMWLANCompanion.kext missing"
        ((errors++))
    fi
    
    # Check WiFiAgent
    if [[ -d "$CORESERVICES_DIR/$WIFI_AGENT" ]]; then
        success "✓ WiFiAgent.app installed"
    else
        error "✗ WiFiAgent.app missing"
        ((errors++))
    fi
    
    # Check firmware files
    local firmware_count=0
    if [[ -f "$FIRMWARE_DIR/brcmfmac4350-pcie_7.35.180.119.bin" ]]; then
        success "✓ BCM4350 firmware installed"
        ((firmware_count++))
    fi
    
    if [[ -f "$FIRMWARE_DIR/brcmfmac43602-pcie_7.35.177.61.bin" ]]; then
        success "✓ BCM43602 firmware installed"
        ((firmware_count++))
    fi
    
    if [[ $firmware_count -eq 0 ]]; then
        error "✗ No firmware files installed"
        ((errors++))
    fi
    
    return $errors
}

# Main installation function
main() {
    echo "=========================================="
    echo "AppleBCMWLANCompanion Smart Installer"
    echo "for macOS 26 (Tahoe)"
    echo "=========================================="
    echo
    
    # Pre-installation checks
    check_root
    check_macos_version
    check_sip
    check_lilu
    detect_hardware
    
    echo
    log "Starting installation..."
    
    # Create backup
    backup_existing
    
    # Install components
    install_kext
    install_wifi_agent
    install_firmware
    
    # Post-installation
    rebuild_cache
    
    echo
    if verify_installation; then
        success "Installation completed successfully!"
        echo
        echo "Next steps:"
        echo "1. Reboot your system"
        echo "2. Check that Wi-Fi is working"
        echo "3. If issues occur, check system logs for errors"
        echo
        echo "For troubleshooting, see: AppleBCMWLANCompanion-Installation-Guide.md"
    else
        error "Installation completed with errors"
        echo "Please check the output above and retry if necessary"
        exit 1
    fi
}

# Run main function
main "$@"