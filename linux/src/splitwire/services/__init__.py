"""
Service modules for SplitWire-Turkey Linux.

This package contains service managers for:
- WireGuard VPN with WGCF/WARP integration (Phase 2)
- Split tunneling (app-based routing) (Phase 2)
- Zapret DPI bypass (Phase 3)
- Blockcheck scanner (Phase 3)
- ByeDPI proxy (Phase 4)
- Proxy routing (Phase 4)
- DNS management with DoH support (Phase 5)
- Discord repair and alternative clients (Phase 6)
- systemd service management (Phase 8)
"""

from .base import (
    BaseService,
    SystemdService,
    ServiceStatus,
    ServiceType,
    ServiceInfo,
)

from .wireguard import (
    WireGuardService,
    WireGuardInterface,
    WGCFAccount,
    get_wireguard_service,
    WIREGUARD_CONFIG_DIR,
    SPLITWIRE_CONFIG_FILE,
)

from .split_tunnel import (
    SplitTunnelService,
    SplitTunnelConfig,
    TunneledApp,
    get_split_tunnel_service,
    KNOWN_APPS,
    BROWSER_APPS,
)

from .zapret import (
    ZapretService,
    ZapretConfig,
    ZapretPreset,
    ZapretMode,
    get_zapret_service,
    DEFAULT_PRESETS,
)

from .blockcheck import (
    BlockcheckService,
    BlockcheckResult,
    ScanMode,
    ScanStatus,
    ScanProgress,
    get_blockcheck_service,
)

from .byedpi import (
    ByeDPIService,
    ByeDPIConfig,
    ByeDPIPreset,
    ByeDPIMode,
    get_byedpi_service,
    DEFAULT_PRESETS as BYEDPI_PRESETS,
)

from .proxy_route import (
    ProxyRouteService,
    ProxyRouteConfig,
    ProxiedApp,
    ProxyMethod,
    get_proxy_route_service,
)

from .dns import (
    DNSService,
    DNSConfig,
    DNSServer,
    DNSBackup,
    DNSManager,
    DoHMode,
    DNS_PRESETS,
    get_dns_service,
)

from .discord import (
    DiscordService,
    DiscordConfig,
    DiscordInstallation,
    WebCordInstallation,
    DiscordVersion,
    InstallMethod,
    RepairResult,
    get_discord_service,
)

from .systemd import (
    SystemdManager,
    SystemdUnitType,
    SystemdActiveState,
    SystemdEnabledState,
    SystemdUnitStatus,
    JournalEntry,
    get_systemd_manager,
)

__all__ = [
    # base
    "BaseService",
    "SystemdService",
    "ServiceStatus",
    "ServiceType",
    "ServiceInfo",
    # wireguard
    "WireGuardService",
    "WireGuardInterface",
    "WGCFAccount",
    "get_wireguard_service",
    "WIREGUARD_CONFIG_DIR",
    "SPLITWIRE_CONFIG_FILE",
    # split_tunnel
    "SplitTunnelService",
    "SplitTunnelConfig",
    "TunneledApp",
    "get_split_tunnel_service",
    "KNOWN_APPS",
    "BROWSER_APPS",
    # zapret
    "ZapretService",
    "ZapretConfig",
    "ZapretPreset",
    "ZapretMode",
    "get_zapret_service",
    "DEFAULT_PRESETS",
    # blockcheck
    "BlockcheckService",
    "BlockcheckResult",
    "ScanMode",
    "ScanStatus",
    "ScanProgress",
    "get_blockcheck_service",
    # byedpi
    "ByeDPIService",
    "ByeDPIConfig",
    "ByeDPIPreset",
    "ByeDPIMode",
    "get_byedpi_service",
    "BYEDPI_PRESETS",
    # proxy_route
    "ProxyRouteService",
    "ProxyRouteConfig",
    "ProxiedApp",
    "ProxyMethod",
    "get_proxy_route_service",
    # dns
    "DNSService",
    "DNSConfig",
    "DNSServer",
    "DNSBackup",
    "DNSManager",
    "DoHMode",
    "DNS_PRESETS",
    "get_dns_service",
    # discord
    "DiscordService",
    "DiscordConfig",
    "DiscordInstallation",
    "WebCordInstallation",
    "DiscordVersion",
    "InstallMethod",
    "RepairResult",
    "get_discord_service",
    # systemd
    "SystemdManager",
    "SystemdUnitType",
    "SystemdActiveState",
    "SystemdEnabledState",
    "SystemdUnitStatus",
    "JournalEntry",
    "get_systemd_manager",
]
