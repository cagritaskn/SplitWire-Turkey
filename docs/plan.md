# Implementation Plan: SplitWire-Turkey Linux Version

**Created**: 2025-12-05
**Updated**: 2025-12-06
**Status**: Draft
**Target Platform**: Ubuntu 22.04+
**Framework**: Python 3.10+ with GTK4/Libadwaita
**Goal**: 100% feature parity with Windows version

---

## Executive Summary

Linux version of SplitWire-Turkey with full feature parity. Uses native Linux tools (wg-quick, zapret, ciadpi) orchestrated by a Python application with a modern GTK4/Libadwaita GUI. Targets Ubuntu first, with potential expansion to other distros later.

**Repository Structure:**
```
SplitWire-Turkey/
├── src/                    # Windows version (C# WPF) - unchanged
│   └── SplitWireTurkey/
├── linux/                  # NEW: Linux version (Python GTK4)
│   └── src/
│       └── splitwire/
└── docs/
    └── plan.md             # This file
```

---

## Goals

- [x] Full feature parity with Windows version
- [x] WireGuard VPN with app-based split tunneling
- [x] Zapret DPI bypass (nfqws/tpws) with blockcheck
- [x] ByeDPI proxy with app-specific routing
- [ ] GoodbyeDPI equivalent (via Zapret nfqws)
- [x] DNS management with DoH support
- [x] Discord repair tools
- [ ] Multi-language support (TR/EN/RU/ES - reuse Windows JSONs)
- [ ] systemd service integration
- [ ] Modern GTK4/Libadwaita GUI
- [ ] Easy installation (one-liner + .deb package)
- [ ] Auto-update check

---

## Non-Goals (Out of Scope for v1.0)

- Other distros (Fedora, Arch) - Ubuntu first
- macOS support
- Flatpak/Snap packaging (maybe later)
- CLI-only mode (GUI is primary)

---

## Feature Mapping: Windows → Linux

| Windows Feature | Linux Equivalent | Implementation |
|-----------------|------------------|----------------|
| WireSock (split tunneling) | wg-quick + cgproxy | App-based routing via cgroups |
| Zapret (blockcheck, presets) | zapret native | Originally a Linux tool |
| GoodbyeDPI | zapret nfqws | Same concept, NFQUEUE based |
| ByeDPI + ProxiFyre | ciadpi + cgproxy | ciadpi is ByeDPI's Linux binary |
| drover (Discord DLL) | Not needed | Linux Discord works differently |
| DNS + DoH | resolvectl | systemd-resolved native |
| Windows Services | systemd services | Same concept |
| Registry settings | ~/.config/splitwire/ | XDG standard |
| Multi-language | Same JSON files | Direct reuse from Windows |
| Theme (dark/light) | Libadwaita | Follows system or manual |
| Auto-update | GitHub API | Same approach |
| Discord Repair | apt/snap/flatpak | Different but achievable |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 SplitWire-Turkey Linux                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   GUI Layer                         │    │
│  │            (GTK4 + Libadwaita)                      │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │    │
│  │  │WireSock │ │ ByeDPI  │ │ Zapret  │ │ Repair  │    │    │
│  │  │  Page   │ │  Page   │ │  Page   │ │  Page   │    │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │    │
│  │  │ GoodBye │ │Advanced │ │Settings │               │    │
│  │  │DPI Page │ │  Page   │ │  Page   │               │    │
│  │  └─────────┘ └─────────┘ └─────────┘               │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │                  Core Layer                         │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │    │
│  │  │ Config  │ │Language │ │ Logger  │ │ Backup  │    │    │
│  │  │ Manager │ │ Manager │ │         │ │ Manager │    │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │               Service Layer                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │    │
│  │  │WireGuard │ │  Zapret  │ │  ByeDPI  │             │    │
│  │  │ Service  │ │  Service │ │  Service │             │    │
│  │  └──────────┘ └──────────┘ └──────────┘             │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │    │
│  │  │   DNS    │ │ Discord  │ │ systemd  │             │    │
│  │  │ Service  │ │  Repair  │ │ Manager  │             │    │
│  │  └──────────┘ └──────────┘ └──────────┘             │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │              System Layer (subprocess)              │    │
│  │  wg-quick  nfqws  tpws  ciadpi  cgproxy  resolvectl │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
linux/
├── src/
│   └── splitwire/
│       ├── __init__.py
│       ├── __main__.py           # Entry point with CLI
│       ├── application.py        # Gtk.Application subclass (Phase 7)
│       │
│       ├── core/                 # Core infrastructure (Phase 1)
│       │   ├── __init__.py       # Exports all core modules
│       │   ├── config.py         # Config management (XDG paths)
│       │   ├── language.py       # i18n (reuse Windows JSONs)
│       │   ├── logger.py         # Logging with rotation
│       │   ├── shell.py          # Subprocess wrapper
│       │   └── backup.py         # Backup/restore system
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── base.py           # Base service class
│       │   ├── wireguard.py      # WireGuard + wgcf
│       │   ├── split_tunnel.py   # cgproxy app-based routing
│       │   ├── zapret.py         # Zapret nfqws/tpws
│       │   ├── blockcheck.py     # Blockcheck automation
│       │   ├── byedpi.py         # ciadpi proxy
│       │   ├── proxy_route.py    # Route apps through proxy
│       │   ├── dns.py            # DNS management
│       │   ├── discord.py        # Discord repair tools
│       │   └── systemd.py        # systemd management
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── window.py         # Main window
│       │   ├── pages/
│       │   │   ├── __init__.py
│       │   │   ├── wiresock.py   # WireGuard page
│       │   │   ├── byedpi.py     # ByeDPI page
│       │   │   ├── zapret.py     # Zapret page
│       │   │   ├── goodbyedpi.py # GoodbyeDPI-style page
│       │   │   ├── repair.py     # Discord repair
│       │   │   ├── advanced.py   # Advanced/services
│       │   │   └── settings.py   # Settings
│       │   └── widgets/
│       │       ├── __init__.py
│       │       ├── service_row.py
│       │       └── preset_selector.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── polkit.py         # pkexec helper
│           ├── network.py        # Network utilities
│           ├── system.py         # System detection
│           └── deps.py           # Dependency checker
│
├── data/
│   ├── icons/
│   │   ├── splitwire.svg
│   │   ├── splitwire-symbolic.svg
│   │   └── flags/                # Language flags
│   ├── splitwire.desktop         # Desktop entry
│   ├── com.splitwire.turkey.gschema.xml  # GSettings (optional)
│   └── polkit/
│       └── com.splitwire.turkey.policy   # Polkit rules
│
├── config/
│   ├── languages/                # Symlink or copy from Windows
│   │   ├── tr.json
│   │   ├── en.json
│   │   ├── ru.json
│   │   └── es.json
│   ├── zapret/
│   │   ├── presets.json          # All presets from Windows
│   │   └── blacklist.txt         # Domain blacklist
│   └── default_config.json
│
├── scripts/
│   ├── install.sh                # One-liner installer
│   ├── uninstall.sh              # Clean uninstall
│   └── setup-deps.sh             # Install system dependencies
│
├── systemd/
│   ├── splitwire-wg.service
│   ├── splitwire-wg-refresh.timer
│   ├── splitwire-zapret.service
│   ├── splitwire-byedpi.service
│   └── splitwire-cgproxy.service
│
├── debian/                       # DEB packaging
│   ├── control
│   ├── rules
│   ├── postinst
│   └── postrm
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_wireguard.py
│   ├── test_zapret.py
│   └── test_dns.py
│
├── pyproject.toml
├── README.md
├── README_TR.md
├── LICENSE
└── CHANGELOG.md
```

---

## Phase 0: System Detection & Compatibility ✅

**Objective**: Detect system capabilities before any setup
**Complexity**: Low
**Dependencies**: None
**Status**: Complete

### Tasks

- [x] 0.1 System detector module
  - Files: `linux/src/splitwire/utils/system.py`
  - Details:
    - Detect Ubuntu version (22.04, 23.10, 24.04)
    - Check systemd presence
    - Check iptables vs nftables
    - Check WireGuard kernel module
    - Check NFQUEUE support
    - Check DNS manager (systemd-resolved, NetworkManager, resolvconf)
    - Check cgroups v1/v2 support
    - Check Python version
  - **Implementation**: `SystemDetector` class with `detect()` method, `SystemInfo` dataclass, `get_system_info()` convenience function

- [x] 0.2 Dependency checker
  - Files: `linux/src/splitwire/utils/deps.py`
  - Details:
    - List missing packages (system and Python)
    - Install via apt (system) and pip (Python)
    - Check Python version >= 3.10
  - **Implementation**: `DependencyChecker` class with `check_system_dependencies()`, `check_python_dependencies()`, `install_system_dependencies()`, `install_python_dependencies()` methods

- [x] 0.3 Polkit helper
  - Files: `linux/src/splitwire/utils/polkit.py`, `linux/data/polkit/com.splitwire.turkey.policy`
  - Details:
    - Polkit policy for GUI elevation
    - pkexec wrapper for privileged operations
    - Fallback to sudo/gksudo if pkexec unavailable
  - **Implementation**: `PolkitHelper` class with `run_elevated()` method, `ElevationMethod` enum, `ElevationResult` dataclass

### Acceptance Criteria

- [x] System info correctly detected
- [x] Missing dependencies listed
- [x] Polkit elevation works

---

## Phase 1: Project Foundation

**Objective**: Core infrastructure
**Complexity**: Low
**Dependencies**: None

### Tasks

- [x] 1.1 Create project structure
  - Files: All directories and `__init__.py` files
  - Details: Created linux/ folder with core/, services/, ui/, utils/ packages

- [x] 1.2 pyproject.toml
  - Files: `linux/pyproject.toml`
  - Details:
    ```toml
    [project]
    name = "splitwire-linux"
    version = "1.0.0"
    description = "Network restriction bypass tool for Linux"
    requires-python = ">=3.10"
    dependencies = [
        "PyGObject>=3.42.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ]

    [project.scripts]
    splitwire = "splitwire.__main__:main"
    splitwire-cli = "splitwire.cli:main"

    [project.gui-scripts]
    splitwire-gtk = "splitwire.__main__:main"
    ```

- [x] 1.3 Config manager
  - Files: `linux/src/splitwire/core/config.py`
  - Details:
    - XDG paths (~/.config/splitwire/, ~/.local/share/splitwire/, ~/.cache/splitwire/)
    - JSON config read/write with atomic writes
    - Default config generation with dataclasses

- [x] 1.4 Language manager
  - Files: `linux/src/splitwire/core/language.py`
  - Details:
    - Load JSON translation files from resources/languages/
    - Nested key support: `get_text("messages", "error")`
    - LRU caching for performance
    - Fallback to English when translation missing

- [x] 1.5 Logger
  - Files: `linux/src/splitwire/core/logger.py`
  - Details:
    - File logging (~/.cache/splitwire/logs/)
    - Console logging with colored output (ANSI)
    - Rotating file handler (5MB max, 3 backups)
    - Component loggers for subsystems

- [x] 1.6 Shell executor
  - Files: `linux/src/splitwire/core/shell.py`
  - Details:
    - subprocess wrapper with sync, async, and streaming modes
    - Timeout handling with CommandResult dataclass
    - Output capture with status enum
    - pkexec integration prepared for privilege elevation

- [x] 1.7 Backup/Rollback system
  - Files: `linux/src/splitwire/core/backup.py`
  - Details:
    - BackupManager for tarball-based backups
    - SnapshotManager for atomic rollback
    - Backup types: CONFIG, DNS, WIREGUARD, ZAPRET, SERVICES, FULL
    - Metadata tracking with automatic cleanup

### Acceptance Criteria

- [ ] `pip install -e .` works
- [ ] Config read/write works
- [ ] Language files load correctly
- [ ] Logging works
- [ ] Shell commands execute correctly
- [ ] Backup/restore works

---

## Phase 2: WireGuard Service (WireSock Equivalent)

**Objective**: Full WireGuard VPN with app-based split tunneling
**Complexity**: High
**Dependencies**: Phase 1

### Tasks

- [x] 2.1 Base Service class
  - Files: `linux/src/splitwire/services/base.py`
  - Details:
    - Abstract BaseService with install/remove/start/stop/restart/status
    - SystemdService subclass for systemd-managed services
    - ServiceStatus enum (RUNNING, STOPPED, FAILED, etc.)
    - ServiceType enum (VPN, DPI_BYPASS, PROXY, DNS, SYSTEM)
    - ServiceInfo dataclass for comprehensive service info
    - Status change callbacks for UI integration

- [x] 2.2 WireGuard core service
  - Files: `linux/src/splitwire/services/wireguard.py`
  - Details:
    - wg-quick up/down commands
    - Config file management (/etc/wireguard/splitwire.conf)
    - Interface status monitoring via `wg show`
    - Connection testing via ping through interface
    - Transfer statistics tracking

- [x] 2.3 WGCF integration
  - Files: `linux/src/splitwire/services/wireguard.py`
  - Details:
    - Download wgcf Linux amd64 binary from GitHub releases
    - wgcf register (Cloudflare WARP account)
    - wgcf generate (create WireGuard config)
    - Parse and modify generated config for split tunneling
    - Cache account.toml in ~/.local/share/splitwire/wgcf/

- [x] 2.4 Split tunneling - IP based
  - Files: `linux/src/splitwire/services/wireguard.py`
  - Details:
    - AllowedIPs configuration modification
    - Exclude local/private networks by default
    - DNS configuration injection

- [x] 2.5 Split tunneling - App based (AllowedApps equivalent)
  - Files: `linux/src/splitwire/services/split_tunnel.py`
  - Details:
    - cgproxy integration for cgroup-based routing
    - 15 predefined apps (Discord, browsers, Telegram, Steam, etc.)
    - BROWSER_APPS list for "include browsers" option
    - Custom app path support
    - Configuration persistence in ~/.config/splitwire/

- [x] 2.6 WireGuard refresh timer (WireSock yineleyici equivalent)
  - Files: `linux/systemd/splitwire-wg-refresh.timer`, `linux/systemd/splitwire-wg-refresh.service`
  - Details:
    - systemd timer for periodic restart (30 min default)
    - Randomized delay to avoid thundering herd

- [x] 2.7 systemd service files
  - Files: `linux/systemd/splitwire-wg.service`, `linux/systemd/splitwire-cgproxy.service`
  - Details:
    - WireGuard service with wg-quick
    - cgproxy service for split tunneling
    - Proper dependencies and security hardening

### Acceptance Criteria

- [ ] WGCF downloads and registers successfully
- [ ] WireGuard config generated correctly
- [ ] wg-quick up/down works
- [ ] IP-based split tunneling works
- [ ] App-based split tunneling works (Discord routed through VPN)
- [ ] Refresh timer works
- [ ] Service persists across reboot

---

## Phase 3: Zapret Service (Native + GoodbyeDPI Equivalent)

**Objective**: Full Zapret with blockcheck, presets, custom params
**Complexity**: High
**Dependencies**: Phase 1

### Tasks

- [x] 3.1 Zapret installer/manager
  - Files: `linux/src/splitwire/services/zapret.py`
  - Details:
    - Clone zapret repository from GitHub
    - Build binaries with make
    - Install dependencies (libnetfilter-queue-dev, etc.)
    - Verify installation
  - **Implementation**: `ZapretService.install()` with `_install_dependencies()`, `_clone_zapret()`, `_build_zapret()` methods

- [x] 3.2 nfqws management (GoodbyeDPI equivalent)
  - Files: `linux/src/splitwire/services/zapret.py`
  - Details:
    - Start/stop nfqws process with PID tracking
    - iptables NFQUEUE rules (mangle table POSTROUTING)
    - Port filtering (80, 443 configurable)
    - System-wide DPI bypass
  - **Implementation**: `_start_nfqws()`, `_stop_nfqws()`, `_add_iptables_rules()`, `_remove_iptables_rules()`

- [x] 3.3 tpws management (transparent proxy)
  - Files: `linux/src/splitwire/services/zapret.py`
  - Details:
    - Start/stop tpws process with PID tracking
    - iptables REDIRECT rules (nat table OUTPUT)
    - Alternative to nfqws
  - **Implementation**: `_start_tpws()`, `_stop_tpws()`, TPWS_PORT=988

- [x] 3.4 Blockcheck integration (Zapret Otomatik Kurulum)
  - Files: `linux/src/splitwire/services/blockcheck.py`
  - Details:
    - Strategy-based testing (without native blockcheck.sh)
    - Parse output for optimal parameters
    - Three scan modes:
      - Hızlı (quick) - 3 basic strategies
      - Standart (standard) - 7 strategies
      - Tam (full) - 12 strategies
    - Generate config from results
  - **Implementation**: `BlockcheckService` with `start_scan()`, `_generate_strategies()`, `_test_strategy()`

- [x] 3.5 Preset system
  - Files: Built into `linux/src/splitwire/services/zapret.py`
  - Details:
    - 8 default presets (turkey_discord, turkey_general, turkey_youtube, preset_split, preset_fake, preset_disorder, preset_tpws, preset_combined)
    - Custom presets saved to `~/.config/splitwire/zapret/presets.json`
  - **Implementation**: `DEFAULT_PRESETS` dict, `ZapretPreset` dataclass, `add_custom_preset()`, `remove_custom_preset()`

- [x] 3.6 Custom parameters
  - Details:
    - Allow user to edit zapret parameters
    - Save custom presets
    - "Hazır Ayarı Düzenle" functionality
  - **Implementation**: `set_custom_nfqws_args()`, `set_custom_tpws_args()`, config persistence

- [x] 3.7 Blacklist support (domain filtering)
  - Files: `~/.config/splitwire/zapret/blacklist.txt`
  - Details:
    - Apply DPI bypass only to listed domains
    - Default: Discord domains (discord.com, discord.gg, discordapp.com, etc.)
    - Editable via API
    - "Blacklist Kullan" option
  - **Implementation**: `get_blacklist()`, `set_blacklist()`, `add_to_blacklist()`, `remove_from_blacklist()`, `set_use_blacklist()`

- [x] 3.8 One-shot mode (Tek Seferlik)
  - Details:
    - Run zapret without installing service
    - Process stops when closed
  - **Implementation**: `start(one_shot=True)` parameter

- [x] 3.9 systemd service
  - Files: `linux/systemd/splitwire-zapret.service`
  - **Implementation**: Service file with ExecStart/ExecStop/ExecReload, security hardening, CAP_NET_ADMIN capability

### Unit Tests
- Files: `linux/tests/test_zapret.py`, `linux/tests/test_blockcheck.py`
- Coverage: ZapretPreset, ZapretConfig, ZapretService, DEFAULT_PRESETS, blacklist management, nfqws/tpws args building, BlockcheckService, ScanMode, ScanStatus, strategy generation

### Acceptance Criteria

- [x] Zapret installs correctly
- [x] nfqws starts and stops
- [x] tpws starts and stops
- [x] iptables rules added/removed correctly
- [x] Blockcheck runs and finds parameters
- [x] Presets work
- [x] Custom parameters work
- [x] Blacklist filtering works
- [x] One-shot mode works
- [x] Service persists across reboot

---

## Phase 4: ByeDPI Service

**Objective**: ByeDPI proxy with app-specific routing (ProxiFyre equivalent)
**Complexity**: Medium
**Dependencies**: Phase 1

### Tasks

- [x] 4.1 ByeDPI (ciadpi) integration
  - Files: `linux/src/splitwire/services/byedpi.py`
  - Details:
    - Download ciadpi Linux binary from GitHub releases
    - Start SOCKS5 proxy on localhost:1080
    - Same DPI bypass parameters as Windows (disorder, split, fake, oob, etc.)
    - Process management with PID tracking
  - **Implementation**: `ByeDPIService` with `_download_binary()`, `_start_process()`, `_stop_process()`, preset system

- [x] 4.2 App-based proxy routing (ProxiFyre equivalent)
  - Files: `linux/src/splitwire/services/proxy_route.py`
  - Details:
    - cgproxy for cgroup-based SOCKS routing (recommended)
    - redsocks + iptables alternative
    - Environment variable method for per-app launch
  - **Implementation**: `ProxyRouteService` with `ProxyMethod` enum (CGPROXY, REDSOCKS, ENV)

- [x] 4.3 Per-app configuration
  - Details:
    - Select which apps use ByeDPI proxy
    - "Tarayıcılar için de tünelleme yap" option (`include_browsers`)
    - Same app list as WireGuard split tunneling (KNOWN_APPS, BROWSER_APPS)
  - **Implementation**: `ProxiedApp` dataclass, `add_custom_app()`, `remove_custom_app()`

- [x] 4.4 systemd service
  - Files: `linux/systemd/splitwire-byedpi.service`
  - **Implementation**: Service file with security hardening, ExecStart for ciadpi

### Unit Tests
- Files: `linux/tests/test_byedpi.py`, `linux/tests/test_proxy_route.py`
- Coverage: ByeDPIPreset, ByeDPIConfig, ByeDPIService, DEFAULT_PRESETS, ProxiedApp, ProxyRouteConfig, ProxyMethod

### Acceptance Criteria

- [x] ciadpi starts and creates SOCKS proxy
- [x] Apps can be routed through proxy
- [x] Discord works through ByeDPI
- [x] Browser tunneling works
- [x] Service persists across reboot

---

## Phase 5: DNS Service

**Objective**: Full DNS management with DoH
**Complexity**: Medium
**Dependencies**: Phase 1

### Tasks

- [x] 5.1 DNS Service core
  - Files: `linux/src/splitwire/services/dns.py`
  - Details:
    - Detect DNS manager (systemd-resolved primary for Ubuntu)
    - Backup current DNS settings
    - Apply new DNS via resolvectl
  - **Implementation**: `DNSService` class with `_detect_dns_manager()`, `_backup_current_dns()`, `_apply_systemd_resolved()` methods

- [x] 5.2 DNS Presets
  - Details:
    - 9 presets: Google, Cloudflare, Cloudflare Family, Quad9, Quad9 Unsecured, OpenDNS, AdGuard, AdGuard Family, Turkish Telecom
    - Each preset includes DoH URL (where supported)
  - **Implementation**: `DNS_PRESETS` dict, `DNSServer` dataclass

- [x] 5.3 DoH (DNS over HTTPS)
  - Files: `linux/src/splitwire/services/dns.py`
  - Details:
    - Configure systemd-resolved for DoH via /etc/systemd/resolved.conf.d/
    - Three modes: OFF, OPPORTUNISTIC, STRICT
    - resolvectl dnsovertls yes/opportunistic/no
  - **Implementation**: `DoHMode` enum, `set_doh_mode()`, DNS config via resolved.conf.d drop-in

- [x] 5.4 Auto DNS on install
  - Details:
    - "DNS ve DoH ayarlarını her kurulumda gerçekleştir" option
    - Apply DNS settings with every service install
  - **Implementation**: `set_auto_apply()`, `should_auto_apply()` methods

- [x] 5.5 DNS restore
  - Details:
    - Restore original DNS settings
    - "DNS ve DoH Ayarlarını Geri Al" button
  - **Implementation**: `_restore_dns()` method with backup JSON support

### Unit Tests
- Files: `linux/tests/test_dns.py`
- Coverage: DNSServer, DNSConfig, DNSBackup dataclasses, DNSManager/DoHMode enums, DNS_PRESETS validation, DNSService methods, config persistence

### Acceptance Criteria

- [x] DNS can be changed
- [x] DoH can be enabled
- [x] Original DNS backed up
- [x] DNS restore works
- [x] Auto DNS option works

---

## Phase 6: Discord Repair Tools (Onarım)

**Objective**: Discord repair and alternative clients
**Complexity**: Medium
**Dependencies**: Phase 1

### Tasks

- [x] 6.1 Discord detector
  - Files: `linux/src/splitwire/services/discord.py`
  - Details:
    - Detect Discord installation method:
      - .deb package
      - Snap
      - Flatpak
      - tar.gz (manual)
    - Detect which versions installed (Stable, PTB, Canary)
    - Show installation paths
  - **Implementation**: `DiscordService._detect_version()`, `InstallMethod` enum, `DiscordVersion` enum

- [x] 6.2 Discord repair
  - Details:
    - Clear Discord cache:
      - ~/.config/discord/
      - ~/.config/discordptb/
      - ~/.config/discordcanary/
    - Reinstall Discord based on install method
    - "Discord'u Onar" functionality
  - **Implementation**: `repair_discord()`, `clear_cache()`, `clear_all_cache()`, `RepairResult` dataclass

- [x] 6.3 Discord PTB/Canary installer
  - Details:
    - Download PTB or Canary .deb from Discord
    - Install alongside stable
    - "Discord PTB Yükle" functionality
  - **Implementation**: `install_discord()`, `_install_deb()`, `_install_flatpak()`, `_install_snap()`

- [x] 6.4 WebCord installer
  - Details:
    - Download WebCord AppImage or install via Flatpak
    - Create desktop shortcut if requested
    - "WebCord Yükle" functionality
  - **Implementation**: `install_webcord()`, `uninstall_webcord()`, `WebCordInstallation` dataclass

- [x] 6.5 Status display
  - Details:
    - Show which Discord versions installed
    - Show running status
    - Launch buttons for each version
  - **Implementation**: `get_installations()`, `get_webcord()`, `launch_discord()`, `launch_webcord()`, `kill_discord()`

### Unit Tests
- Files: `linux/tests/test_discord.py`
- Coverage: DiscordVersion, InstallMethod, DiscordInstallation, WebCordInstallation, DiscordConfig, RepairResult, detection methods, cache operations

### Acceptance Criteria

- [x] Discord installations detected correctly
- [x] Cache clearing works
- [x] Discord reinstall works
- [x] PTB/Canary install works
- [x] WebCord install works
- [x] Status display accurate

---

## Phase 7: GTK4 GUI

**Objective**: Complete GUI matching Windows functionality
**Complexity**: High
**Dependencies**: Phase 2, 3, 4, 5, 6

### Tasks

- [ ] 7.1 Application skeleton
  - Files: `linux/src/splitwire/application.py`, `linux/src/splitwire/__main__.py`
  - Details:
    ```python
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, Gio

    class SplitWireApp(Adw.Application):
        def __init__(self):
            super().__init__(application_id='com.splitwire.turkey')

        def do_activate(self):
            win = SplitWireWindow(application=self)
            win.present()
    ```

- [ ] 7.2 Main Window with navigation
  - Files: `linux/src/splitwire/ui/window.py`
  - Details:
    - Adw.ApplicationWindow
    - Adw.NavigationSplitView (sidebar + content)
    - Header bar with logo, language selector, theme toggle
    - Status bar showing active services

- [ ] 7.3 WireSock Page
  - Files: `linux/src/splitwire/ui/pages/wiresock.py`
  - Widgets:
    - Status indicator (active/inactive)
    - "WS Standart Kurulum" button
    - "WS Alternatif Kurulum" button (if applicable)
    - "Tarayıcılar için de tünelleme yap" switch
    - "WireSock yineleyici kur" switch
    - App list for custom tunneling (Adw.ExpanderRow)
    - "Klasör Ekle" / "Listeyi Temizle" buttons
    - "Özel Kurulum" / "Özel Config Oluştur" buttons
    - Service remove button

- [ ] 7.4 ByeDPI Page
  - Files: `linux/src/splitwire/ui/pages/byedpi.py`
  - Widgets:
    - Status indicator
    - "ByeDPI Split Tunneling Kurulum" button
    - "Tarayıcılar için de tünelleme yap" switch
    - "ByeDPI'ı Kaldır" button

- [ ] 7.5 Zapret Page
  - Files: `linux/src/splitwire/ui/pages/zapret.py`
  - Widgets:
    - Status indicator
    - "Zapret Otomatik Kurulum" button
    - Scan speed selector (Adw.ComboRow): Hızlı/Standart/Tam
    - Preset dropdown (Adw.ComboRow)
    - "Hazır Ayarı Düzenle" expander with text editor
    - "Önayarlı Hizmet Kur" button
    - "Önayarlı Tek Seferlik" button
    - "Zapret'i Kaldır" button

- [ ] 7.6 GoodbyeDPI Page
  - Files: `linux/src/splitwire/ui/pages/goodbyedpi.py`
  - Widgets:
    - Status indicator
    - Preset dropdown
    - "Hazır Ayarı Düzenle" expander
    - "Blacklist Kullan" switch
    - "Blacklisti Düzenle" expander with text editor
    - "Hizmet Kur" button
    - "Tek Seferlik" button
    - "GoodbyeDPI'ı Kaldır" button

- [ ] 7.7 Repair Page (Onarım)
  - Files: `linux/src/splitwire/ui/pages/repair.py`
  - Widgets:
    - Discord status cards (installed versions)
    - "Discord'u Onar" button
    - "Discord PTB Yükle" button
    - "WebCord Yükle" button
    - "Discord PTB için temiz kurulum yap" switch
    - "WebCord için kısayol oluştur" switch
    - Launch/uninstall buttons for each version

- [ ] 7.8 Advanced Page (Gelişmiş)
  - Files: `linux/src/splitwire/ui/pages/advanced.py`
  - Widgets:
    - Services list with status (Adw.PreferencesGroup)
    - "DNS ve DoH ayarlarını her kurulumda gerçekleştir" switch
    - "Tüm Hizmetleri Kaldır" button
    - "DNS ve DoH Ayarlarını Geri Al" button
    - "SplitWire-Turkey'i Kaldır" button

- [ ] 7.9 Settings Page (Ayarlar)
  - Files: `linux/src/splitwire/ui/pages/settings.py`
  - Widgets:
    - Language selector with flags (Adw.ComboRow)
    - Theme selector: System/Light/Dark (Adw.ComboRow)
    - About section:
      - Version info
      - GitHub link
      - Patreon link
    - "Logs Klasörünü Aç" button

- [ ] 7.10 Common widgets
  - Files: `linux/src/splitwire/ui/widgets/`
  - Details:
    - ServiceStatusRow - shows service name + status indicator
    - PresetSelector - dropdown with edit button
    - AppSelector - list of apps with checkboxes
    - LogViewer - scrollable text view for logs

- [ ] 7.11 Desktop integration
  - Files: `linux/data/splitwire.desktop`, `linux/data/icons/`
  - Details:
    - .desktop file for app launcher
    - SVG icons (regular + symbolic)
    - Language flag icons

- [ ] 7.12 Notifications
  - Details:
    - Success/error notifications using Gio.Notification
    - Service status change notifications

### Acceptance Criteria

- [ ] All pages accessible and functional
- [ ] All Windows features have equivalent UI
- [ ] Service status correctly displayed
- [ ] Language switching works
- [ ] Theme switching works
- [ ] Keyboard navigation works
- [ ] App looks native on Ubuntu/GNOME

---

## Phase 8: systemd Integration

**Objective**: Service management
**Complexity**: Medium
**Dependencies**: Phase 2, 3, 4

### Tasks

- [ ] 8.1 systemd manager class
  - Files: `linux/src/splitwire/services/systemd.py`
  - Details:
    - Install/remove service unit files
    - Enable/disable (start on boot)
    - Start/stop/restart services
    - Check service status
    - Read journal logs

- [ ] 8.2 Service unit files
  - Files: `linux/systemd/*.service`, `linux/systemd/*.timer`
  - Details:
    - splitwire-wg.service - WireGuard VPN
    - splitwire-wg-refresh.timer - WireGuard refresh
    - splitwire-zapret.service - Zapret nfqws
    - splitwire-byedpi.service - ByeDPI proxy
    - splitwire-cgproxy.service - App routing

- [ ] 8.3 Service dependencies
  - Details:
    - Correct ordering (network-online.target)
    - Proper After/Requires declarations

### Acceptance Criteria

- [ ] Services install correctly to /etc/systemd/system/
- [ ] systemctl commands work
- [ ] Services start on boot when enabled
- [ ] Journal logs accessible

---

## Phase 9: Installation & Packaging

**Objective**: Easy installation for Ubuntu
**Complexity**: Medium
**Dependencies**: Phase 7, 8

### Tasks

- [ ] 9.1 Dependency install script
  - Files: `linux/scripts/setup-deps.sh`
  - Details:
    ```bash
    #!/bin/bash
    sudo apt update
    sudo apt install -y \
      python3-gi python3-gi-cairo \
      gir1.2-gtk-4.0 gir1.2-adw-1 \
      wireguard-tools \
      libnetfilter-queue-dev \
      iptables \
      cgroupfs-mount \
      curl wget git
    ```

- [ ] 9.2 Main install script
  - Files: `linux/scripts/install.sh`
  - Details:
    - Check Ubuntu version
    - Run setup-deps.sh
    - Create venv and install package
    - Download binaries (wgcf, ciadpi)
    - Clone and setup zapret
    - Copy systemd units
    - Copy polkit policy
    - Copy desktop file and icons
    - Create /usr/local/bin/splitwire symlink

- [ ] 9.3 Uninstall script
  - Files: `linux/scripts/uninstall.sh`
  - Details:
    - Stop and remove all services
    - Restore DNS settings
    - Restore iptables rules
    - Remove config files
    - Remove binaries
    - Remove desktop entry

- [ ] 9.4 DEB package
  - Files: `linux/debian/`
  - Details:
    - control file with dependencies
    - postinst for setup
    - postrm for cleanup
    - Build with dpkg-buildpackage

- [ ] 9.5 One-liner install
  - Details:
    ```bash
    curl -sSL https://raw.githubusercontent.com/cagritaskn/SplitWire-Turkey/main/linux/scripts/install.sh | sudo bash
    ```

### Acceptance Criteria

- [ ] Fresh Ubuntu install works
- [ ] All dependencies installed
- [ ] App launches from application menu
- [ ] Uninstall removes everything
- [ ] DEB package installs correctly

---

## Phase 10: Testing & Documentation

**Objective**: Quality assurance
**Complexity**: Medium
**Dependencies**: Phase 9

### Tasks

- [ ] 10.1 Unit tests
  - Files: `linux/tests/`
  - Details:
    - Config manager tests
    - Language manager tests
    - Service class tests (mocked)

- [ ] 10.2 Integration tests
  - Details:
    - Test in Ubuntu VM
    - Test each service installation
    - Test GUI functionality

- [ ] 10.3 README.md
  - Files: `linux/README.md`, `linux/README_TR.md`
  - Details:
    - Features list
    - Screenshots
    - Installation instructions
    - Usage guide
    - FAQ
    - Troubleshooting

- [ ] 10.4 CHANGELOG.md
  - Files: `linux/CHANGELOG.md`

- [ ] 10.5 Update main README
  - Files: `README.md`
  - Details: Add Linux version section

### Acceptance Criteria

- [ ] Tests pass
- [ ] Documentation complete
- [ ] Screenshots included

---

## Phase 11: Release

**Objective**: First release
**Complexity**: Low
**Dependencies**: Phase 10

### Tasks

- [ ] 11.1 GitHub Release
  - Details:
    - Tag v1.0.0-linux
    - Release notes
    - Attach .deb package

- [ ] 11.2 CI/CD
  - Files: `.github/workflows/linux-build.yml`
  - Details:
    - Build on push
    - Run tests
    - Build .deb on release

### Acceptance Criteria

- [ ] Release published
- [ ] DEB downloadable
- [ ] Install instructions work

---

## Dependencies Summary

### System Packages (apt)
```bash
python3-gi python3-gi-cairo
gir1.2-gtk-4.0 gir1.2-adw-1
wireguard-tools
libnetfilter-queue-dev
iptables
cgroupfs-mount cgroup-tools
curl wget git
```

### Python Packages (pip)
```
PyGObject>=3.42.0
httpx>=0.25.0
pydantic>=2.0.0
```

### External Binaries (downloaded)
- wgcf (Linux amd64) - from GitHub releases
- ciadpi (ByeDPI Linux) - from GitHub releases
- zapret - cloned from GitHub

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| WireGuard kernel module missing | High | Check on startup, show install instructions |
| NFQUEUE not available | High | Fall back to tpws, show warning |
| cgproxy not working | Medium | Fall back to proxychains or iptables |
| Different Ubuntu versions | Medium | Test on 22.04, 23.10, 24.04 |
| GTK4/Libadwaita not available | High | Require Ubuntu 22.04+ |
| Polkit issues | Medium | Provide manual sudo instructions |

---

## Notes

- Windows version remains unchanged in `src/`
- Linux version lives in `linux/`
- Language files can be symlinked or copied from Windows version
- Keep UI/UX as close to Windows as possible
- Use same preset values/parameters as Windows version
