#!/bin/bash
# AppleBCMWLANCompanion Smart Patcher Launcher for macOS 26
# Quick launcher script with safety checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_status $RED "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check macOS version
check_macos_version() {
    local version=$(sw_vers -productVersion)
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    if [[ $major -eq 15 && $minor -ge 5 ]]; then
        print_status $GREEN "macOS version $version is compatible"
        return 0
    else
        print_status $RED "macOS 26 (15.5+) required, found $version"
        return 1
    fi
}

# Function to show menu
show_menu() {
    echo
    print_status $BLUE "AppleBCMWLANCompanion Smart Patcher for macOS 26"
    print_status $BLUE "================================================"
    echo
    echo "1. Run complete patch (recommended)"
    echo "2. Run dry-run test (no changes)"
    echo "3. Test injection system"
    echo "4. Show help"
    echo "5. Exit"
    echo
    read -p "Select option (1-5): " choice
}

# Function to run complete patch
run_complete_patch() {
    print_status $YELLOW "Starting complete AppleBCMWLANCompanion patch..."
    python3 "$SCRIPT_DIR/macos26-bcmwlan-patcher.py"
}

# Function to run dry run
run_dry_run() {
    print_status $YELLOW "Running dry-run test..."
    python3 "$SCRIPT_DIR/macos26-bcmwlan-patcher.py" --dry-run
}

# Function to run tests
run_tests() {
    print_status $YELLOW "Running injection system tests..."
    python3 "$SCRIPT_DIR/test-bcmwlan-injection.py"
}

# Function to show help
show_help() {
    echo
    print_status $BLUE "AppleBCMWLANCompanion Smart Patcher Help"
    print_status $BLUE "======================================="
    echo
    echo "This patcher enables Broadcom WiFi support on macOS 26 by injecting"
    echo "AppleBCMWLANCompanion components into the system."
    echo
    echo "Features:"
    echo "  • Smart injection of AppleBCMWLANCompanion kext"
    echo "  • Binary patching of system frameworks"
    echo "  • Automatic hardware detection"
    echo "  • Comprehensive backup and restore"
    echo "  • macOS 26 compatibility"
    echo
    echo "Supported Hardware:"
    echo "  • BCM43224, BCM43225, BCM43227, BCM43228"
    echo "  • BCM4331, BCM4335, BCM4339"
    echo "  • BCM4352, BCM4353, BCM4356, BCM4358, BCM4359"
    echo "  • BCM4360, BCM43602, BCM4364, BCM4365, BCM4366"
    echo "  • BCM4371, BCM4377, BCM4378, BCM4387, BCM4398"
    echo
    echo "Safety Features:"
    echo "  • Automatic system backup"
    echo "  • Restore script generation"
    echo "  • Dry-run testing mode"
    echo "  • Comprehensive validation"
    echo
    echo "For more information, see README-macOS26-BCMWLAN.md"
    echo
}

# Main execution
main() {
    # Check prerequisites
    check_root
    check_macos_version
    
    # Show welcome message
    print_status $GREEN "Welcome to AppleBCMWLANCompanion Smart Patcher!"
    print_status $YELLOW "This will patch your macOS 26 system for Broadcom WiFi support."
    echo
    
    # Interactive menu
    while true; do
        show_menu
        
        case $choice in
            1)
                run_complete_patch
                break
                ;;
            2)
                run_dry_run
                break
                ;;
            3)
                run_tests
                break
                ;;
            4)
                show_help
                ;;
            5)
                print_status $YELLOW "Exiting..."
                exit 0
                ;;
            *)
                print_status $RED "Invalid option. Please select 1-5."
                ;;
        esac
    done
}

# Handle command line arguments
if [[ $# -gt 0 ]]; then
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --patch)
            check_root
            check_macos_version
            run_complete_patch
            exit 0
            ;;
        --dry-run)
            check_root
            check_macos_version
            run_dry_run
            exit 0
            ;;
        --test)
            check_root
            check_macos_version
            run_tests
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            print_status $YELLOW "Use --help for usage information"
            exit 1
            ;;
    esac
fi

# Run main function
main