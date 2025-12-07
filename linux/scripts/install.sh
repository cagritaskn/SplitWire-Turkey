#!/bin/bash
#
# SplitWire-Turkey Linux - Main Installation Script
# Installs SplitWire-Turkey and all required components.
#
# Usage: sudo ./install.sh [options]
#   --skip-deps     Skip dependency installation
#   --no-desktop    Don't create desktop entry
#   --dev           Install in development mode
#
# One-liner installation:
#   curl -sSL https://raw.githubusercontent.com/cagritaskn/SplitWire-Turkey/main/linux/scripts/install.sh | sudo bash
#

set -e

# Configuration
SPLITWIRE_VERSION="1.0.0"
INSTALL_DIR="/opt/splitwire"
CONFIG_DIR="/etc/splitwire"
DATA_DIR="/usr/share/splitwire"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"
POLKIT_DIR="/usr/share/polkit-1/actions"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor"

# GitHub URLs
GITHUB_REPO="cagritaskn/SplitWire-Turkey"
WGCF_REPO="ViRb3/wgcf"
CIADPI_REPO="hufrea/byedpi"
ZAPRET_REPO="bol-van/zapret"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# Options
SKIP_DEPS=false
NO_DESKTOP=false
DEV_MODE=false

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --no-desktop)
                NO_DESKTOP=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --skip-deps     Skip dependency installation"
                echo "  --no-desktop    Don't create desktop entry"
                echo "  --dev           Install in development mode"
                echo "  --help, -h      Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Check root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Get script directory (for local installs)
get_script_dir() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REPO_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Check if we're in a git repo
    if [[ -d "$REPO_DIR/.git" ]] || [[ -d "$REPO_DIR/src/splitwire" ]]; then
        LOCAL_INSTALL=true
        log_info "Local installation from: $REPO_DIR"
    else
        LOCAL_INSTALL=false
        log_info "Remote installation"
    fi
}

# Install dependencies
install_dependencies() {
    if [[ "$SKIP_DEPS" == true ]]; then
        log_warning "Skipping dependency installation (--skip-deps)"
        return
    fi
    
    log_step "Installing system dependencies..."
    
    if [[ "$LOCAL_INSTALL" == true ]] && [[ -f "$SCRIPT_DIR/setup-deps.sh" ]]; then
        bash "$SCRIPT_DIR/setup-deps.sh"
    else
        # Download and run setup-deps.sh
        curl -sSL "https://raw.githubusercontent.com/$GITHUB_REPO/main/linux/scripts/setup-deps.sh" | bash
    fi
    
    log_success "Dependencies installed"
}

# Create directories
create_directories() {
    log_step "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/bin"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "/var/log/splitwire"
    mkdir -p "/var/run/splitwire"
    
    # User config directory (will be created per-user on first run)
    # ~/.config/splitwire
    # ~/.cache/splitwire
    
    log_success "Directories created"
}

# Download WGCF binary
download_wgcf() {
    log_step "Downloading WGCF..."
    
    local wgcf_path="$INSTALL_DIR/bin/wgcf"
    
    if [[ -f "$wgcf_path" ]]; then
        log_info "WGCF already exists, checking version..."
    fi
    
    # Get latest release
    local latest_url=$(curl -sL "https://api.github.com/repos/$WGCF_REPO/releases/latest" | \
        grep -oP '"browser_download_url": "\K[^"]*linux_amd64[^"]*' | head -1)
    
    if [[ -z "$latest_url" ]]; then
        log_warning "Could not find WGCF release, trying direct download..."
        latest_url="https://github.com/$WGCF_REPO/releases/latest/download/wgcf_linux_amd64"
    fi
    
    curl -sL "$latest_url" -o "$wgcf_path"
    chmod +x "$wgcf_path"
    
    if [[ -x "$wgcf_path" ]]; then
        log_success "WGCF downloaded: $("$wgcf_path" --version 2>&1 | head -1 || echo 'installed')"
    else
        log_warning "WGCF download may have failed"
    fi
}

# Download ciadpi (ByeDPI) binary
download_ciadpi() {
    log_step "Downloading ciadpi (ByeDPI)..."
    
    local ciadpi_path="$INSTALL_DIR/bin/ciadpi"
    
    # Get latest release
    local latest_url=$(curl -sL "https://api.github.com/repos/$CIADPI_REPO/releases/latest" | \
        grep -oP '"browser_download_url": "\K[^"]*linux-x86_64[^"]*\.tar\.gz[^"]*' | head -1)
    
    if [[ -n "$latest_url" ]]; then
        local tmp_dir=$(mktemp -d)
        curl -sL "$latest_url" -o "$tmp_dir/ciadpi.tar.gz"
        tar -xzf "$tmp_dir/ciadpi.tar.gz" -C "$tmp_dir"
        
        # Find the binary
        local bin_file=$(find "$tmp_dir" -name "ciadpi" -type f | head -1)
        if [[ -n "$bin_file" ]]; then
            cp "$bin_file" "$ciadpi_path"
            chmod +x "$ciadpi_path"
        fi
        
        rm -rf "$tmp_dir"
        log_success "ciadpi downloaded"
    else
        log_warning "Could not download ciadpi, will need manual installation"
    fi
}

# Clone and setup Zapret
setup_zapret() {
    log_step "Setting up Zapret..."
    
    local zapret_dir="/opt/zapret"
    
    if [[ -d "$zapret_dir" ]]; then
        log_info "Zapret directory exists, updating..."
        cd "$zapret_dir"
        git pull --quiet 2>/dev/null || log_warning "Could not update zapret"
    else
        git clone --depth 1 "https://github.com/$ZAPRET_REPO.git" "$zapret_dir"
    fi
    
    # Build nfqws if needed
    if [[ -f "$zapret_dir/nfq/Makefile" ]]; then
        log_info "Building nfqws..."
        cd "$zapret_dir/nfq"
        make -j$(nproc) 2>/dev/null || log_warning "nfqws build may have failed"
    fi
    
    # Make scripts executable
    chmod +x "$zapret_dir"/*.sh 2>/dev/null || true
    chmod +x "$zapret_dir/nfq/nfqws" 2>/dev/null || true
    
    log_success "Zapret setup complete"
}

# Install Python package
install_python_package() {
    log_step "Installing SplitWire Python package..."
    
    if [[ "$LOCAL_INSTALL" == true ]]; then
        # Install from local source
        cd "$REPO_DIR"
        
        if [[ "$DEV_MODE" == true ]]; then
            pip3 install -e . --break-system-packages 2>/dev/null || pip3 install -e .
            log_success "Package installed in development mode"
        else
            pip3 install . --break-system-packages 2>/dev/null || pip3 install .
            log_success "Package installed from local source"
        fi
    else
        # Install from GitHub
        pip3 install "git+https://github.com/$GITHUB_REPO.git#subdirectory=linux" \
            --break-system-packages 2>/dev/null || \
        pip3 install "git+https://github.com/$GITHUB_REPO.git#subdirectory=linux"
        log_success "Package installed from GitHub"
    fi
}

# Copy systemd unit files
install_systemd_units() {
    log_step "Installing systemd unit files..."
    
    local source_dir
    if [[ "$LOCAL_INSTALL" == true ]]; then
        source_dir="$REPO_DIR/systemd"
    else
        # Download from GitHub
        source_dir=$(mktemp -d)
        for unit in splitwire-wg.service splitwire-wg-refresh.timer splitwire-wg-refresh.service \
                    splitwire-zapret.service splitwire-byedpi.service splitwire-cgproxy.service; do
            curl -sL "https://raw.githubusercontent.com/$GITHUB_REPO/main/linux/systemd/$unit" \
                -o "$source_dir/$unit"
        done
    fi
    
    # Copy unit files
    if [[ -d "$source_dir" ]]; then
        cp "$source_dir"/*.service "$SYSTEMD_DIR/" 2>/dev/null || true
        cp "$source_dir"/*.timer "$SYSTEMD_DIR/" 2>/dev/null || true
        
        # Reload systemd
        systemctl daemon-reload
        
        log_success "Systemd units installed"
    else
        log_warning "Could not find systemd unit files"
    fi
}

# Install polkit policy
install_polkit_policy() {
    log_step "Installing polkit policy..."
    
    local policy_file="$POLKIT_DIR/com.splitwire.turkey.policy"
    
    cat > "$policy_file" << 'POLICY'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <vendor>SplitWire-Turkey</vendor>
  <vendor_url>https://github.com/cagritaskn/SplitWire-Turkey</vendor_url>

  <action id="com.splitwire.turkey.manage-services">
    <description>Manage SplitWire network services</description>
    <message>Authentication is required to manage SplitWire network services</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
  </action>

  <action id="com.splitwire.turkey.configure-network">
    <description>Configure network settings</description>
    <message>Authentication is required to configure network settings</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
  </action>
</policyconfig>
POLICY
    
    log_success "Polkit policy installed"
}

# Install desktop entry and icons
install_desktop_entry() {
    if [[ "$NO_DESKTOP" == true ]]; then
        log_warning "Skipping desktop entry (--no-desktop)"
        return
    fi
    
    log_step "Installing desktop entry and icons..."
    
    # Desktop entry
    local desktop_file="$DESKTOP_DIR/com.splitwire.turkey.desktop"
    
    cat > "$desktop_file" << 'DESKTOP'
[Desktop Entry]
Name=SplitWire-Turkey
Comment=Network restriction bypass tool for Linux
Comment[tr]=Linux için ağ kısıtlaması bypass aracı
Exec=splitwire
Icon=com.splitwire.turkey
Terminal=false
Type=Application
Categories=Network;Utility;
Keywords=vpn;wireguard;dpi;bypass;discord;dns;proxy;
StartupNotify=true
StartupWMClass=splitwire
DESKTOP
    
    # Copy icons if local install
    if [[ "$LOCAL_INSTALL" == true ]] && [[ -d "$REPO_DIR/data/icons" ]]; then
        cp -r "$REPO_DIR/data/icons/hicolor/"* "$ICON_DIR/"
    else
        # Create a simple icon placeholder
        mkdir -p "$ICON_DIR/scalable/apps"
        # Download icon from GitHub if available
        curl -sL "https://raw.githubusercontent.com/$GITHUB_REPO/main/linux/data/icons/hicolor/scalable/apps/com.splitwire.turkey.svg" \
            -o "$ICON_DIR/scalable/apps/com.splitwire.turkey.svg" 2>/dev/null || true
    fi
    
    # Update icon cache
    gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    
    log_success "Desktop entry installed"
}

# Create launcher symlink
create_launcher() {
    log_step "Creating launcher..."
    
    local launcher="$BIN_DIR/splitwire"
    
    cat > "$launcher" << 'LAUNCHER'
#!/bin/bash
# SplitWire-Turkey Launcher
exec python3 -m splitwire "$@"
LAUNCHER
    
    chmod +x "$launcher"
    
    log_success "Launcher created at $launcher"
}

# Create default config
create_default_config() {
    log_step "Creating default configuration..."
    
    # Main config
    if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        cat > "$CONFIG_DIR/config.json" << 'CONFIG'
{
    "version": "1.0.0",
    "language": "tr",
    "theme": "system",
    "auto_dns": true,
    "dns_server": "cloudflare",
    "doh_enabled": true
}
CONFIG
    fi
    
    # Default blacklist
    if [[ ! -f "$CONFIG_DIR/blacklist.txt" ]]; then
        cat > "$CONFIG_DIR/blacklist.txt" << 'BLACKLIST'
discord.com
discord.gg
discordapp.com
discordapp.net
discord.media
discordcdn.com
BLACKLIST
    fi
    
    # Set permissions
    chmod 644 "$CONFIG_DIR"/*
    
    log_success "Default configuration created"
}

# Verify installation
verify_installation() {
    log_step "Verifying installation..."
    
    local failed=0
    
    # Check launcher
    if command -v splitwire &>/dev/null; then
        log_success "Launcher: OK"
    else
        log_error "Launcher not found"
        failed=1
    fi
    
    # Check Python module
    if python3 -c "import splitwire" &>/dev/null; then
        log_success "Python module: OK"
    else
        log_error "Python module not importable"
        failed=1
    fi
    
    # Check systemd units
    if [[ -f "$SYSTEMD_DIR/splitwire-wg.service" ]]; then
        log_success "Systemd units: OK"
    else
        log_warning "Some systemd units may be missing"
    fi
    
    # Check WGCF
    if [[ -x "$INSTALL_DIR/bin/wgcf" ]]; then
        log_success "WGCF binary: OK"
    else
        log_warning "WGCF binary not found"
    fi
    
    # Check Zapret
    if [[ -d "/opt/zapret" ]]; then
        log_success "Zapret: OK"
    else
        log_warning "Zapret not found"
    fi
    
    return $failed
}

# Print completion message
print_completion() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN} Installation Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "SplitWire-Turkey v$SPLITWIRE_VERSION has been installed."
    echo ""
    echo "To start the application:"
    echo "  - From terminal: splitwire"
    echo "  - From application menu: Search for 'SplitWire'"
    echo ""
    echo "Configuration files: $CONFIG_DIR"
    echo "Log files: /var/log/splitwire"
    echo ""
    echo "To uninstall:"
    echo "  sudo /opt/splitwire/uninstall.sh"
    echo "  or"
    echo "  sudo $SCRIPT_DIR/uninstall.sh"
    echo ""
}

# Main function
main() {
    echo ""
    echo "=========================================="
    echo " SplitWire-Turkey Installer v$SPLITWIRE_VERSION"
    echo "=========================================="
    echo ""
    
    parse_args "$@"
    check_root
    get_script_dir
    
    install_dependencies
    create_directories
    download_wgcf
    download_ciadpi
    setup_zapret
    install_python_package
    install_systemd_units
    install_polkit_policy
    install_desktop_entry
    create_launcher
    create_default_config
    
    echo ""
    if verify_installation; then
        print_completion
    else
        log_warning "Installation completed with some warnings."
        log_warning "Some features may not work correctly."
        print_completion
    fi
}

# Run main function
main "$@"
