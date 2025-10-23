# Makefile for OpenCore Legacy Patcher Privileged Helper Tool

CC = clang
UNAME_S := $(shell uname -s)

# Platform-specific flags
ifeq ($(UNAME_S),Darwin)
    # macOS build
    CFLAGS = -Wall -Wextra -O2 -arch x86_64 -arch arm64
    FRAMEWORKS = -framework Foundation -framework Security
    LIBS = -lxpc
else
    # Cross-compile or Linux build (for testing syntax)
    CFLAGS = -Wall -Wextra -O2
    FRAMEWORKS = 
    LIBS = 
    $(warning Building on non-macOS platform - this is for syntax checking only)
endif

HELPER_NAME = com.sumitduster.opencore-legacy-patcher.privileged-helper
PLIST_NAME = $(HELPER_NAME).plist

INSTALL_DIR = /Library/PrivilegedHelperTools
LAUNCHD_DIR = /Library/LaunchDaemons

.PHONY: all build install clean

all: build

build: $(HELPER_NAME)

$(HELPER_NAME): privileged-helper.c
	$(CC) $(CFLAGS) $(FRAMEWORKS) $(LIBS) -o $(HELPER_NAME) privileged-helper.c

install: build
	@echo "Installing privileged helper tool..."
	sudo cp $(HELPER_NAME) $(INSTALL_DIR)/
	sudo cp $(PLIST_NAME) $(LAUNCHD_DIR)/
	sudo chown root:wheel $(INSTALL_DIR)/$(HELPER_NAME)
	sudo chown root:wheel $(LAUNCHD_DIR)/$(PLIST_NAME)
	sudo chmod 755 $(INSTALL_DIR)/$(HELPER_NAME)
	sudo chmod 644 $(LAUNCHD_DIR)/$(PLIST_NAME)
	@echo "Privileged helper tool installed successfully"

uninstall:
	@echo "Uninstalling privileged helper tool..."
	sudo launchctl unload $(LAUNCHD_DIR)/$(PLIST_NAME) 2>/dev/null || true
	sudo rm -f $(INSTALL_DIR)/$(HELPER_NAME)
	sudo rm -f $(LAUNCHD_DIR)/$(PLIST_NAME)
	@echo "Privileged helper tool uninstalled"

clean:
	rm -f $(HELPER_NAME)

load:
	sudo launchctl load $(LAUNCHD_DIR)/$(PLIST_NAME)

unload:
	sudo launchctl unload $(LAUNCHD_DIR)/$(PLIST_NAME)

reload: unload load

status:
	sudo launchctl list | grep $(HELPER_NAME) || echo "Helper not loaded"