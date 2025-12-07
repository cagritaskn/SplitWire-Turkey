#!/bin/bash
#
# SplitWire-Turkey Linux - Dependency Installation Script
# This script installs all required system dependencies for SplitWire-Turkey.
#
# Usage: sudo ./setup-deps.sh
#
# Supports: Ubuntu 22.04+, Linux Mint 21+, Debian 12+
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
        DISTRO_CODENAME=$VERSION_CODENAME
    else
        log_error "Cannot detect distribution. /etc/os-release not found."
        exit 1
    fi
    
    log_info "Detected: $DISTRO $DISTRO_VERSION ($DISTRO_CODENAME)"
}

# Check Ubuntu/Debian version compatibility
check_compatibility() {
    case $DISTRO in
        ubuntu)
            if [[ "${DISTRO_VERSION%%.*}" -lt 22 ]]; then
                log_error "Ubuntu 22.04 or later is required (found: $DISTRO_VERSION)"
                exit 1
            fi
            ;;
        linuxmint)
            if [[ "${DISTRO_VERSION%%.*}" -lt 21 ]]; then
                log_error "Linux Mint 21 or later is required (found: $DISTRO_VERSION)"
                exit 1
            fi
            ;;
        debian)
            if [[ "${DISTRO_VERSION%%.*}" -lt 12 ]]; then
                log_error "Debian 12 or later is required (found: $DISTRO_VERSION)"
                exit 1
            fi
            ;;
        pop)
            log_info "Pop!_OS detected, treating as Ubuntu-based"
            ;;
        *)
            log_warning "Unknown distribution: $DISTRO. Attempting installation anyway..."
            ;;
    esac
}

# Update package lists
update_packages() {
    log_info "Updating package lists..."
    apt-get update -qq
    log_success "Package lists updated"
}

# Install core dependencies
install_core_deps() {
    log_info "Installing core dependencies..."
    
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        curl \
        wget \
        git \
        ca-certificates \
        gnupg \
        lsb-release
    
    log_success "Core dependencies installed"
}

# Install GTK4 and Libadwaita for GUI
install_gtk_deps() {
    log_info "Installing GTK4 and Libadwaita dependencies..."
    
    apt-get install -y \
        python3-gi \
        python3-gi-cairo \
        gir1.2-gtk-4.0 \
        gir1.2-adw-1 \
        libgtk-4-dev \
        libadwaita-1-dev \
        gettext
    
    log_success "GTK4/Libadwaita dependencies installed"
}

# Install WireGuard tools
install_wireguard() {
    log_info "Installing WireGuard tools..."
    
    apt-get install -y \
        wireguard-tools \
        wireguard
    
    # Load WireGuard kernel module if not loaded
    if ! lsmod | grep -q wireguard; then
        modprobe wireguard 2>/dev/null || log_warning "Could not load wireguard module (may need reboot)"
    fi
    
    log_success "WireGuard tools installed"
}

# Install network tools for DPI bypass
install_network_deps() {
    log_info "Installing network tools for DPI bypass..."
    
    apt-get install -y \
        iptables \
        iptables-persistent \
        netfilter-persistent \
        libnetfilter-queue-dev \
        libnetfilter-queue1 \
        libnfnetlink-dev \
        nftables \
        iproute2 \
        net-tools \
        dnsutils
    
    log_success "Network tools installed"
}

# Install cgroup tools for split tunneling
install_cgroup_deps() {
    log_info "Installing cgroup tools for split tunneling..."
    
    apt-get install -y \
        cgroup-tools \
        cgroupfs-mount || log_warning "cgroup packages may have different names on this system"
    
    # Ensure cgroups are mounted
    if [[ ! -d /sys/fs/cgroup ]]; then
        log_warning "cgroups not mounted. Attempting to mount..."
        mount -t cgroup2 none /sys/fs/cgroup 2>/dev/null || true
    fi
    
    log_success "Cgroup tools installed"
}

# Install additional utilities
install_utils() {
    log_info "Installing additional utilities..."
    
    apt-get install -y \
        jq \
        unzip \
        tar \
        gzip \
        xdg-utils \
        libcap2-bin \
        policykit-1
    
    log_success "Additional utilities installed"
}

# Install Python packages via pip (if needed)
install_python_packages() {
    log_info "Installing Python packages..."
    
    # These are typically available via apt, but we ensure they're installed
    apt-get install -y \
        python3-requests \
        python3-yaml \
        python3-cryptography \
        python3-httpx 2>/dev/null || true
    
    log_success "Python packages installed"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local failed=0
    
    # Check Python
    if python3 --version &>/dev/null; then
        log_success "Python3: $(python3 --version)"
    else
        log_error "Python3 not found"
        failed=1
    fi
    
    # Check GTK4
    if python3 -c "import gi; gi.require_version('Gtk', '4.0')" &>/dev/null; then
        log_success "GTK4 Python bindings: OK"
    else
        log_error "GTK4 Python bindings not working"
        failed=1
    fi
    
    # Check Libadwaita
    if python3 -c "import gi; gi.require_version('Adw', '1')" &>/dev/null; then
        log_success "Libadwaita Python bindings: OK"
    else
        log_error "Libadwaita Python bindings not working"
        failed=1
    fi
    
    # Check WireGuard
    if command -v wg &>/dev/null; then
        log_success "WireGuard: $(wg --version 2>&1 | head -1)"
    else
        log_error "WireGuard tools not found"
        failed=1
    fi
    
    # Check iptables
    if command -v iptables &>/dev/null; then
        log_success "iptables: $(iptables --version)"
    else
        log_error "iptables not found"
        failed=1
    fi
    
    return $failed
}

# Main function
main() {
    echo ""
    echo "=========================================="
    echo " SplitWire-Turkey Dependency Installer"
    echo "=========================================="
    echo ""
    
    check_root
    detect_distro
    check_compatibility
    
    echo ""
    log_info "Installing dependencies..."
    echo ""
    
    update_packages
    install_core_deps
    install_gtk_deps
    install_wireguard
    install_network_deps
    install_cgroup_deps
    install_utils
    install_python_packages
    
    echo ""
    log_info "Verifying installation..."
    echo ""
    
    if verify_installation; then
        echo ""
        log_success "All dependencies installed successfully!"
        echo ""
        echo "You can now run the main installation script:"
        echo "  sudo ./install.sh"
        echo ""
    else
        echo ""
        log_error "Some dependencies failed to install."
        echo "Please check the errors above and try again."
        exit 1
    fi
}

# Run main function
main "$@"
