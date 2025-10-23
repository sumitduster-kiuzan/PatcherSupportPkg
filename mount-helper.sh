#!/bin/bash

# Mount Helper Script for OpenCore Legacy Patcher
# This script helps handle sudo password requirements when mounting volumes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenCore Legacy Patcher Mount Helper${NC}"
echo "This script helps resolve sudo password issues when mounting volumes."
echo

# Function to check if running with sudo
check_sudo() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${GREEN}✓ Running with sudo privileges${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Not running with sudo privileges${NC}"
        return 1
    fi
}

# Function to configure sudo for passwordless mounting
configure_sudo_mount() {
    echo -e "${YELLOW}Configuring sudo for passwordless mounting...${NC}"
    
    # Create sudoers entry for mount commands
    SUDOERS_ENTRY="$USER ALL=(ALL) NOPASSWD: /sbin/mount, /sbin/umount, /usr/sbin/diskutil"
    SUDOERS_FILE="/etc/sudoers.d/oclp-mount"
    
    if check_sudo; then
        echo "$SUDOERS_ENTRY" > "$SUDOERS_FILE"
        chmod 440 "$SUDOERS_FILE"
        echo -e "${GREEN}✓ Sudo configuration updated${NC}"
        echo "You can now run mount commands without password prompts."
    else
        echo -e "${RED}✗ Need sudo privileges to configure passwordless mounting${NC}"
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Function to remove sudo configuration
remove_sudo_config() {
    echo -e "${YELLOW}Removing sudo configuration...${NC}"
    
    SUDOERS_FILE="/etc/sudoers.d/oclp-mount"
    
    if check_sudo; then
        if [ -f "$SUDOERS_FILE" ]; then
            rm "$SUDOERS_FILE"
            echo -e "${GREEN}✓ Sudo configuration removed${NC}"
        else
            echo -e "${YELLOW}⚠ No sudo configuration found${NC}"
        fi
    else
        echo -e "${RED}✗ Need sudo privileges to remove configuration${NC}"
        echo "Please run: sudo $0 --remove"
        exit 1
    fi
}

# Function to test mount capabilities
test_mount() {
    echo -e "${YELLOW}Testing mount capabilities...${NC}"
    
    # Test if we can run mount commands without password
    if sudo -n /sbin/mount 2>/dev/null; then
        echo -e "${GREEN}✓ Can run mount commands without password${NC}"
    else
        echo -e "${RED}✗ Cannot run mount commands without password${NC}"
        echo "Run with --configure to set up passwordless mounting."
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --configure    Configure sudo for passwordless mounting"
    echo "  --remove       Remove sudo configuration"
    echo "  --test         Test current mount capabilities"
    echo "  --help         Show this help message"
    echo
    echo "Examples:"
    echo "  sudo $0 --configure    # Set up passwordless mounting"
    echo "  $0 --test              # Test if mounting works"
    echo "  sudo $0 --remove       # Remove configuration"
}

# Main script logic
case "${1:-}" in
    --configure)
        configure_sudo_mount
        ;;
    --remove)
        remove_sudo_config
        ;;
    --test)
        test_mount
        ;;
    --help)
        show_usage
        ;;
    "")
        echo -e "${YELLOW}No option specified. Use --help for usage information.${NC}"
        echo
        show_usage
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_usage
        exit 1
        ;;
esac