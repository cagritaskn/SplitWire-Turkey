"""
SplitWire-Turkey Linux

Network restriction bypass tool for Ubuntu/Linux.

This package provides:
- WireGuard VPN with split tunneling (via cgproxy)
- Zapret DPI bypass (nfqws/tpws)
- ByeDPI/ciadpi proxy
- DNS management with DoH support
"""

__version__ = "1.0.0"
__author__ = "SplitWire-Turkey Contributors"
__license__ = "MIT"

# Version info tuple
VERSION_INFO = (1, 0, 0)


def get_version() -> str:
    """Get version string."""
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """Get version as tuple."""
    return VERSION_INFO
