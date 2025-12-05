"""
Utility modules for SplitWire-Turkey Linux.

This package contains:
- system: System detection and compatibility checking
- deps: Dependency checking and installation
- polkit: Privilege escalation helpers
"""

from .system import (
    SystemDetector,
    SystemInfo,
    UbuntuVersion,
    FirewallBackend,
    InitSystem,
    DNSManager,
    get_system_info,
    print_system_info,
)

from .deps import (
    DependencyChecker,
    Dependency,
    DependencyStatus,
    check_dependencies,
    print_dependency_status,
    install_all_dependencies,
)

from .polkit import (
    PolkitHelper,
    ElevationMethod,
    ElevationResult,
    get_polkit_helper,
    run_elevated,
    can_elevate,
    is_root,
)

__all__ = [
    # system
    "SystemDetector",
    "SystemInfo",
    "UbuntuVersion",
    "FirewallBackend",
    "InitSystem",
    "DNSManager",
    "get_system_info",
    "print_system_info",
    # deps
    "DependencyChecker",
    "Dependency",
    "DependencyStatus",
    "check_dependencies",
    "print_dependency_status",
    "install_all_dependencies",
    # polkit
    "PolkitHelper",
    "ElevationMethod",
    "ElevationResult",
    "get_polkit_helper",
    "run_elevated",
    "can_elevate",
    "is_root",
]
