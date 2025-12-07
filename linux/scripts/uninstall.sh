#!/bin/bash
#
# SplitWire-Turkey Linux - Uninstallation Script
# Removes SplitWire-Turkey and all its components.
#
# Usage: sudo ./uninstall.sh [options]
#   --keep-config   Keep configuration files
#   --keep-zapret   Keep Zapret installation
#   --purge         Remove everything including user data
#

set -e

# Configuration (same as install.sh)
INSTALL_DIR="/opt/splitwire"
CONFIG_DIR="/etc/splitwire"
DATA_DIR="/usr/share/splitwire"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"
POLKIT_DIR="/usr/share/polkit-1/actions"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor"

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
KEEP_CONFIG=false
KEEP_ZAPRET=false
PURGE=false

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --keep-config)
                KEEP_CONFIG=true
                shift
                ;;
            --keep-zapret)
                KEEP_ZAPRET=true
                shift
                ;;
            --purge)
                PURGE=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --keep-config   Keep configuration files"
                echo "  --keep-zapret   Keep Zapret installation"
                echo "  --purge         Remove everything including user data"
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

# Confirm uninstallation
confirm_uninstall() {
    echo ""
    log_warning "This will remove SplitWire-Turkey from your system."
    echo ""
    
    if [[ "$PURGE" == true ]]; then
        log_warning "PURGE mode: All data including user configurations will be removed!"
    fi
    
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled."
        exit 0
    fi
}

# Stop all SplitWire services
stop_services() {
    log_step "Stopping SplitWire services..."
    
    local services=(
        "splitwire-wg.service"
        "splitwire-wg-refresh.timer"
        "splitwire-wg-refresh.service"
        "splitwire-zapret.service"
        "splitwire-byedpi.service"
        "splitwire-cgproxy.service"
    )
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log_info "Stopping $service..."
            systemctl stop "$service" 2>/dev/null || true
        fi
        if systemctl is-enabled --quiet "$service" 2>/dev/null; then
            log_info "Disabling $service..."
            systemctl disable "$service" 2>/dev/null || true
        fi
    done
    
    log_success "Services stopped"
}

# Remove systemd unit files
remove_systemd_units() {
    log_step "Removing systemd unit files..."
    
    local units=(
        "splitwire-wg.service"
        "splitwire-wg-refresh.timer"
        "splitwire-wg-refresh.service"
        "splitwire-zapret.service"
        "splitwire-byedpi.service"
        "splitwire-cgproxy.service"
    )
    
    for unit in "${units[@]}"; do
        if [[ -f "$SYSTEMD_DIR/$unit" ]]; then
            rm -f "$SYSTEMD_DIR/$unit"
            log_info "Removed $unit"
        fi
    done
    
    # Reload systemd
    systemctl daemon-reload
    systemctl reset-failed 2>/dev/null || true
    
    log_success "Systemd units removed"
}

# Restore DNS settings
restore_dns() {
    log_step "Restoring DNS settings..."
    
    # Check for DNS backup
    if [[ -f "/etc/resolv.conf.splitwire.bak" ]]; then
        cp "/etc/resolv.conf.splitwire.bak" "/etc/resolv.conf"
        rm -f "/etc/resolv.conf.splitwire.bak"
        log_success "DNS settings restored from backup"
    else
        log_info "No DNS backup found, skipping"
    fi
    
    # Remove any systemd-resolved overrides we may have added
    if [[ -f "/etc/systemd/resolved.conf.d/splitwire.conf" ]]; then
        rm -f "/etc/systemd/resolved.conf.d/splitwire.conf"
        systemctl restart systemd-resolved 2>/dev/null || true
        log_info "Removed resolved.conf override"
    fi
}

# Clean up iptables rules
cleanup_iptables() {
    log_step "Cleaning up iptables rules..."
    
    # Remove SPLITWIRE_ZAPRET chain
    if iptables -t mangle -L SPLITWIRE_ZAPRET &>/dev/null; then
        iptables -t mangle -D POSTROUTING -j SPLITWIRE_ZAPRET 2>/dev/null || true
        iptables -t mangle -F SPLITWIRE_ZAPRET 2>/dev/null || true
        iptables -t mangle -X SPLITWIRE_ZAPRET 2>/dev/null || true
        log_info "Removed SPLITWIRE_ZAPRET chain"
    fi
    
    # Remove SPLITWIRE_CGPROXY chain
    if iptables -t mangle -L SPLITWIRE_CGPROXY &>/dev/null; then
        iptables -t mangle -D OUTPUT -j SPLITWIRE_CGPROXY 2>/dev/null || true
        iptables -t mangle -F SPLITWIRE_CGPROXY 2>/dev/null || true
        iptables -t mangle -X SPLITWIRE_CGPROXY 2>/dev/null || true
        log_info "Removed SPLITWIRE_CGPROXY chain"
    fi
    
    # Remove routing rules
    ip rule del fwmark 0x1 table 100 2>/dev/null || true
    ip route del local 0.0.0.0/0 dev lo table 100 2>/dev/null || true
    
    # Save iptables
    netfilter-persistent save 2>/dev/null || true
    
    log_success "iptables rules cleaned up"
}

# Remove WireGuard configuration
remove_wireguard_config() {
    log_step "Removing WireGuard configuration..."
    
    # Bring down WireGuard interface if up
    if ip link show splitwire &>/dev/null; then
        wg-quick down splitwire 2>/dev/null || true
        log_info "Brought down WireGuard interface"
    fi
    
    # Remove config file
    if [[ -f "/etc/wireguard/splitwire.conf" ]]; then
        rm -f "/etc/wireguard/splitwire.conf"
        log_info "Removed WireGuard config"
    fi
    
    log_success "WireGuard configuration removed"
}

# Remove Python package
remove_python_package() {
    log_step "Removing Python package..."
    
    pip3 uninstall -y splitwire 2>/dev/null || \
    pip3 uninstall -y splitwire --break-system-packages 2>/dev/null || \
    log_warning "Could not uninstall Python package (may not be installed via pip)"
    
    log_success "Python package removed"
}

# Remove binaries
remove_binaries() {
    log_step "Removing binaries..."
    
    # Remove launcher
    if [[ -f "$BIN_DIR/splitwire" ]]; then
        rm -f "$BIN_DIR/splitwire"
        log_info "Removed launcher"
    fi
    
    # Remove install directory
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        log_info "Removed $INSTALL_DIR"
    fi
    
    log_success "Binaries removed"
}

# Remove Zapret
remove_zapret() {
    if [[ "$KEEP_ZAPRET" == true ]]; then
        log_warning "Keeping Zapret installation (--keep-zapret)"
        return
    fi
    
    log_step "Removing Zapret..."
    
    if [[ -d "/opt/zapret" ]]; then
        rm -rf "/opt/zapret"
        log_info "Removed /opt/zapret"
    fi
    
    log_success "Zapret removed"
}

# Remove desktop entry and icons
remove_desktop_entry() {
    log_step "Removing desktop entry and icons..."
    
    # Remove desktop file
    if [[ -f "$DESKTOP_DIR/com.splitwire.turkey.desktop" ]]; then
        rm -f "$DESKTOP_DIR/com.splitwire.turkey.desktop"
        log_info "Removed desktop entry"
    fi
    
    # Remove icons
    find "$ICON_DIR" -name "com.splitwire.turkey*" -delete 2>/dev/null || true
    
    # Update caches
    gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    
    log_success "Desktop entry removed"
}

# Remove polkit policy
remove_polkit_policy() {
    log_step "Removing polkit policy..."
    
    if [[ -f "$POLKIT_DIR/com.splitwire.turkey.policy" ]]; then
        rm -f "$POLKIT_DIR/com.splitwire.turkey.policy"
        log_info "Removed polkit policy"
    fi
    
    log_success "Polkit policy removed"
}

# Remove configuration files
remove_config() {
    if [[ "$KEEP_CONFIG" == true ]]; then
        log_warning "Keeping configuration files (--keep-config)"
        return
    fi
    
    log_step "Removing configuration files..."
    
    if [[ -d "$CONFIG_DIR" ]]; then
        rm -rf "$CONFIG_DIR"
        log_info "Removed $CONFIG_DIR"
    fi
    
    if [[ -d "$DATA_DIR" ]]; then
        rm -rf "$DATA_DIR"
        log_info "Removed $DATA_DIR"
    fi
    
    log_success "Configuration files removed"
}

# Remove log files
remove_logs() {
    log_step "Removing log files..."
    
    if [[ -d "/var/log/splitwire" ]]; then
        rm -rf "/var/log/splitwire"
        log_info "Removed /var/log/splitwire"
    fi
    
    if [[ -d "/var/run/splitwire" ]]; then
        rm -rf "/var/run/splitwire"
        log_info "Removed /var/run/splitwire"
    fi
    
    log_success "Log files removed"
}

# Remove user data (purge mode)
remove_user_data() {
    if [[ "$PURGE" != true ]]; then
        return
    fi
    
    log_step "Removing user data (purge mode)..."
    
    # Find and remove user config directories
    for home_dir in /home/*; do
        if [[ -d "$home_dir" ]]; then
            local user=$(basename "$home_dir")
            
            # Remove user config
            if [[ -d "$home_dir/.config/splitwire" ]]; then
                rm -rf "$home_dir/.config/splitwire"
                log_info "Removed config for user: $user"
            fi
            
            # Remove user cache
            if [[ -d "$home_dir/.cache/splitwire" ]]; then
                rm -rf "$home_dir/.cache/splitwire"
                log_info "Removed cache for user: $user"
            fi
            
            # Remove user data
            if [[ -d "$home_dir/.local/share/splitwire" ]]; then
                rm -rf "$home_dir/.local/share/splitwire"
                log_info "Removed data for user: $user"
            fi
        fi
    done
    
    # Also check root
    rm -rf /root/.config/splitwire 2>/dev/null || true
    rm -rf /root/.cache/splitwire 2>/dev/null || true
    rm -rf /root/.local/share/splitwire 2>/dev/null || true
    
    log_success "User data removed"
}

# Print completion message
print_completion() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN} Uninstallation Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "SplitWire-Turkey has been removed from your system."
    echo ""
    
    if [[ "$KEEP_CONFIG" == true ]]; then
        echo "Configuration files were kept at: $CONFIG_DIR"
    fi
    
    if [[ "$KEEP_ZAPRET" == true ]]; then
        echo "Zapret was kept at: /opt/zapret"
    fi
    
    echo ""
    echo "Thank you for using SplitWire-Turkey!"
    echo ""
}

# Main function
main() {
    echo ""
    echo "=========================================="
    echo " SplitWire-Turkey Uninstaller"
    echo "=========================================="
    echo ""
    
    parse_args "$@"
    check_root
    confirm_uninstall
    
    stop_services
    remove_systemd_units
    restore_dns
    cleanup_iptables
    remove_wireguard_config
    remove_python_package
    remove_binaries
    remove_zapret
    remove_desktop_entry
    remove_polkit_policy
    remove_config
    remove_logs
    remove_user_data
    
    print_completion
}

# Run main function
main "$@"
