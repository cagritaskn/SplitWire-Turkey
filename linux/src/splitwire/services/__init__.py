"""
Service modules for SplitWire-Turkey Linux.

This package contains service managers for:
- WireGuard VPN with WGCF/WARP integration
- Split tunneling (app-based routing)
- Zapret DPI bypass (Phase 3)
- ByeDPI proxy (Phase 4)
- DNS management (Phase 5)
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
]
