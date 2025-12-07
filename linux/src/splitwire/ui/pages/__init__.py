"""
SplitWire-Turkey UI Pages.

Contains all application pages:
- MainPage: WireGuard/WireSock setup
- ByeDPIPage: ByeDPI proxy setup
- ZapretPage: Zapret DPI bypass
- GoodbyeDPIPage: GoodbyeDPI (nfqws on Linux)
- RepairPage: Discord repair tools
- AdvancedPage: Advanced service management
- SettingsPage: Application settings
"""

from .main_page import MainPage
from .byedpi_page import ByeDPIPage
from .zapret_page import ZapretPage
from .goodbyedpi_page import GoodbyeDPIPage
from .repair_page import RepairPage
from .advanced_page import AdvancedPage
from .settings_page import SettingsPage

__all__ = [
    "MainPage",
    "ByeDPIPage",
    "ZapretPage",
    "GoodbyeDPIPage",
    "RepairPage",
    "AdvancedPage",
    "SettingsPage",
]
