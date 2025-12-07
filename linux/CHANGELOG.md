# Changelog

All notable changes to SplitWire-Turkey Linux will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added

#### Core Infrastructure (Phase 1)
- Configuration management system with JSON-based storage
- Multi-language support (Turkish, English, Russian, Spanish)
- Logging system with rotation and level filtering
- Shell command execution wrapper with timeout support
- Backup and restore functionality for system settings

#### WireGuard Service (Phase 2)
- WireGuard VPN integration via Cloudflare WARP
- WGCF profile generation and management
- Split tunneling support for application-specific routing
- Automatic connection refresh via systemd timer
- Interface management (up/down/status)

#### Zapret Service (Phase 3)
- Zapret installation and management
- nfqws (netfilter queue) for DPI bypass
- tpws (transparent proxy) as alternative method
- Blockcheck-style strategy scanning
- 8 preset configurations for Turkey
- Custom parameter support
- Domain blacklist filtering
- One-shot mode for temporary bypass

#### ByeDPI Service (Phase 4)
- ciadpi (ByeDPI for Linux) integration
- SOCKS5 proxy on localhost
- Multiple DPI bypass strategies
- Custom arguments support

#### Split Tunneling (Phase 5)
- cgroups v2 based application routing
- iptables/nftables rule management
- Application-specific VPN routing
- Process tracking and management

#### DNS Service (Phase 6)
- DNS configuration management
- DNS over HTTPS (DoH) support
- Multiple providers: Cloudflare, Google, Quad9, AdGuard
- Automatic backup and restore of DNS settings
- systemd-resolved integration

#### Discord Service (Phase 6)
- Discord installation detection
- Discord repair functionality
- Alternative client support (Discord PTB, WebCord)
- Cache clearing utilities

#### GTK4 GUI (Phase 7)
- Modern GTK4/Libadwaita interface
- Main page with quick actions
- Zapret configuration page
- ByeDPI configuration page
- GoodbyeDPI-style page (Zapret-based)
- Discord repair page
- Advanced settings page
- Settings page with theme/language options

#### systemd Integration (Phase 8)
- SystemdManager for comprehensive service control
- Service unit files for all components:
  - splitwire-wg.service (WireGuard VPN)
  - splitwire-wg-refresh.timer (Connection refresh)
  - splitwire-zapret.service (DPI bypass)
  - splitwire-byedpi.service (Proxy)
  - splitwire-cgproxy.service (App routing)
- Journal log access
- Security hardening with capability restrictions

#### Installation & Packaging (Phase 9)
- Dependency installation script (setup-deps.sh)
- Main installation script (install.sh)
- Uninstallation script (uninstall.sh)
- Debian package support
- One-liner installation via curl

### Supported Distributions
- Ubuntu 22.04, 23.04, 23.10, 24.04
- Debian 12 (Bookworm)
- Linux Mint 21, 21.1, 21.2, 21.3
- Pop!_OS 22.04

### Dependencies
- Python 3.10+
- GTK4 + Libadwaita
- WireGuard tools
- iptables
- cgroup-tools
- libnetfilter-queue (for Zapret)

### External Tools
- wgcf - WireGuard Cloudflare WARP
- zapret - DPI bypass toolkit
- ciadpi - ByeDPI for Linux

---

## [Unreleased]

### Planned
- Flatpak packaging
- AppImage distribution
- Arch Linux / AUR support
- Fedora / RPM support
- System tray indicator
- Auto-update functionality
- Connection quality monitoring
- Bandwidth statistics

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2025-01 | Initial Release |

---

## Migration Notes

### From Windows Version

The Linux version provides equivalent functionality to the Windows version:

| Windows Feature | Linux Equivalent |
|-----------------|------------------|
| WireSock | WireGuard (wg-quick) |
| GoodbyeDPI | Zapret (nfqws) |
| ByeDPI + ProxiFyre | ciadpi + cgproxy |
| Windows Services | systemd services |
| Registry settings | JSON config files |

### Configuration Migration

Configuration files are stored in:
- System config: `/etc/splitwire/`
- User config: `~/.config/splitwire/`

The configuration format is compatible across platforms.
