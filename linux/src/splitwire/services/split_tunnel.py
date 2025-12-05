"""
App-based split tunneling for SplitWire-Turkey Linux.

Uses cgproxy (cgroup-based routing) to route specific applications
through the VPN tunnel while allowing other traffic to bypass it.

This is the Linux equivalent of WireSock's AllowedApps functionality.
"""

import os
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .base import BaseService, ServiceStatus, ServiceType
from splitwire.core import get_logger, get_shell


# cgproxy configuration
CGPROXY_CONFIG_DIR = Path("/etc/cgproxy")
CGPROXY_CONFIG_FILE = CGPROXY_CONFIG_DIR / "config.json"
CGPROXY_SERVICE = "cgproxy.service"

# Local configuration
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire"
APPS_CONFIG_FILE = LOCAL_CONFIG_DIR / "tunneled_apps.json"

# Known application paths - Linux equivalents of Windows apps
KNOWN_APPS = {
    # Discord
    "discord": [
        "/usr/share/discord/Discord",
        "/usr/bin/discord",
        "/opt/discord/Discord",
        "/snap/discord/current/usr/share/discord/Discord",
        "/var/lib/flatpak/app/com.discordapp.Discord/current/active/files/discord/Discord",
    ],
    "discord-ptb": [
        "/usr/share/discord-ptb/DiscordPTB",
        "/usr/bin/discord-ptb",
    ],
    "discord-canary": [
        "/usr/share/discord-canary/DiscordCanary",
        "/usr/bin/discord-canary",
    ],
    # Browsers
    "firefox": [
        "/usr/lib/firefox/firefox",
        "/usr/bin/firefox",
        "/snap/firefox/current/usr/lib/firefox/firefox",
    ],
    "chrome": [
        "/opt/google/chrome/google-chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ],
    "chromium": [
        "/usr/lib/chromium-browser/chromium-browser",
        "/usr/bin/chromium-browser",
        "/snap/chromium/current/usr/lib/chromium-browser/chromium-browser",
    ],
    "brave": [
        "/opt/brave.com/brave/brave-browser",
        "/usr/bin/brave-browser",
    ],
    "vivaldi": [
        "/opt/vivaldi/vivaldi",
        "/usr/bin/vivaldi",
    ],
    "opera": [
        "/usr/lib/x86_64-linux-gnu/opera/opera",
        "/usr/bin/opera",
    ],
    "edge": [
        "/opt/microsoft/msedge/msedge",
        "/usr/bin/microsoft-edge",
    ],
    # Communication
    "telegram": [
        "/opt/telegram/Telegram",
        "/usr/bin/telegram-desktop",
        "/snap/telegram-desktop/current/bin/Telegram",
    ],
    "signal": [
        "/opt/Signal/signal-desktop",
        "/usr/bin/signal-desktop",
    ],
    "slack": [
        "/usr/lib/slack/slack",
        "/usr/bin/slack",
        "/snap/slack/current/usr/lib/slack/slack",
    ],
    # Gaming
    "steam": [
        "/usr/lib/steam/steam",
        "/usr/bin/steam",
        "/snap/steam/current/usr/lib/steam/steam",
    ],
    # Media
    "spotify": [
        "/usr/share/spotify/spotify",
        "/usr/bin/spotify",
        "/snap/spotify/current/usr/share/spotify/spotify",
    ],
}

# Browser app names for the "include browsers" option
BROWSER_APPS = ["firefox", "chrome", "chromium", "brave", "vivaldi", "opera", "edge"]


@dataclass
class TunneledApp:
    """Information about an app configured for tunneling."""
    name: str
    path: str
    enabled: bool = True
    is_custom: bool = False


@dataclass
class SplitTunnelConfig:
    """Split tunnel configuration."""
    enabled: bool = False
    include_browsers: bool = False
    apps: list[TunneledApp] = field(default_factory=list)
    custom_paths: list[str] = field(default_factory=list)


class SplitTunnelService(BaseService):
    """
    App-based split tunneling using cgproxy.

    cgproxy uses cgroups v2 to route traffic from specific processes
    through a designated network interface (e.g., WireGuard).

    Features:
    - Route specific apps through VPN
    - Predefined app list (Discord, browsers, etc.)
    - Custom app path support
    - Include/exclude browsers option
    """

    def __init__(self):
        """Initialize split tunnel service."""
        super().__init__(
            name="split-tunnel",
            display_name="Split Tunneling",
            description="App-based VPN routing via cgproxy",
            service_type=ServiceType.SYSTEM,
        )
        self._config = SplitTunnelConfig()
        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load tunneled apps configuration."""
        if APPS_CONFIG_FILE.exists():
            try:
                data = json.loads(APPS_CONFIG_FILE.read_text())
                self._config.enabled = data.get("enabled", False)
                self._config.include_browsers = data.get("include_browsers", False)
                self._config.custom_paths = data.get("custom_paths", [])

                self._config.apps = []
                for app_data in data.get("apps", []):
                    self._config.apps.append(TunneledApp(
                        name=app_data.get("name", ""),
                        path=app_data.get("path", ""),
                        enabled=app_data.get("enabled", True),
                        is_custom=app_data.get("is_custom", False),
                    ))
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save tunneled apps configuration."""
        data = {
            "enabled": self._config.enabled,
            "include_browsers": self._config.include_browsers,
            "custom_paths": self._config.custom_paths,
            "apps": [
                {
                    "name": app.name,
                    "path": app.path,
                    "enabled": app.enabled,
                    "is_custom": app.is_custom,
                }
                for app in self._config.apps
            ]
        }
        APPS_CONFIG_FILE.write_text(json.dumps(data, indent=2))

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, apps: Optional[list[str]] = None,
                include_browsers: bool = False,
                interface: str = "splitwire",
                **kwargs) -> bool:
        """
        Install and configure split tunneling.

        Args:
            apps: List of app names or paths to tunnel
            include_browsers: Include common browsers
            interface: Network interface to route through

        Returns:
            True if installation successful
        """
        self._logger.info("Installing split tunneling")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Check dependencies
            if not self._check_dependencies():
                return False

            # Build app list
            tunnel_apps = self._build_app_list(apps, include_browsers)
            if not tunnel_apps:
                self._logger.warning("No apps to tunnel")
                return False

            # Generate cgproxy config
            if not self._generate_cgproxy_config(tunnel_apps, interface):
                return False

            # Start cgproxy service
            if not self.start():
                return False

            # Save configuration
            self._config.enabled = True
            self._config.include_browsers = include_browsers
            self._config.apps = tunnel_apps
            self._save_config()

            self._logger.info("Split tunneling installed successfully")
            return True

        except Exception as e:
            self._logger.exception(f"Installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """Remove split tunneling configuration."""
        self._logger.info("Removing split tunneling")

        try:
            # Stop cgproxy
            if self.is_running():
                self.stop()

            # Remove cgproxy config
            if CGPROXY_CONFIG_FILE.exists():
                result = self._run_privileged(["rm", "-f", str(CGPROXY_CONFIG_FILE)])
                if not result.success:
                    self._logger.warning(f"Failed to remove config: {result.stderr}")

            # Update local config
            self._config.enabled = False
            self._save_config()

            self._logger.info("Split tunneling removed")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.exception(f"Removal failed: {e}")
            return False

    def start(self) -> bool:
        """Start cgproxy service."""
        self._logger.info("Starting cgproxy")

        result = self._run_privileged(
            ["systemctl", "start", CGPROXY_SERVICE],
            timeout=30
        )

        if result.success:
            self._logger.info("cgproxy started")
            self._notify_status_change(ServiceStatus.RUNNING)
            return True
        else:
            self._logger.error(f"Failed to start cgproxy: {result.stderr}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def stop(self) -> bool:
        """Stop cgproxy service."""
        self._logger.info("Stopping cgproxy")

        result = self._run_privileged(
            ["systemctl", "stop", CGPROXY_SERVICE],
            timeout=30
        )

        if result.success:
            self._logger.info("cgproxy stopped")
            self._notify_status_change(ServiceStatus.STOPPED)
            return True
        else:
            self._logger.error(f"Failed to stop cgproxy: {result.stderr}")
            return False

    def status(self) -> ServiceStatus:
        """Get cgproxy service status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        result = self._shell.run(
            ["systemctl", "is-active", CGPROXY_SERVICE],
            timeout=10
        )

        stdout = result.stdout.strip().lower()
        if stdout == "active":
            return ServiceStatus.RUNNING
        elif stdout == "inactive":
            return ServiceStatus.STOPPED
        elif stdout == "failed":
            return ServiceStatus.FAILED
        else:
            return ServiceStatus.UNKNOWN

    def is_installed(self) -> bool:
        """Check if cgproxy is configured."""
        return CGPROXY_CONFIG_FILE.exists() and self._config.enabled

    # =========================================================================
    # Split tunnel specific methods
    # =========================================================================

    def get_known_apps(self) -> dict[str, list[str]]:
        """Get dictionary of known apps and their paths."""
        return KNOWN_APPS.copy()

    def get_available_apps(self) -> list[TunneledApp]:
        """
        Get list of apps available for tunneling.

        Returns apps that are actually installed on the system.
        """
        available = []

        for app_name, paths in KNOWN_APPS.items():
            for path in paths:
                if Path(path).exists():
                    available.append(TunneledApp(
                        name=app_name,
                        path=path,
                        enabled=False,
                        is_custom=False,
                    ))
                    break  # Only add first found path for each app

        return available

    def get_tunneled_apps(self) -> list[TunneledApp]:
        """Get list of currently tunneled apps."""
        return [app for app in self._config.apps if app.enabled]

    def add_custom_app(self, name: str, path: str) -> bool:
        """
        Add a custom app to tunnel list.

        Args:
            name: App display name
            path: Full path to executable

        Returns:
            True if added successfully
        """
        if not Path(path).exists():
            self._logger.error(f"Path does not exist: {path}")
            return False

        # Check if already added
        for app in self._config.apps:
            if app.path == path:
                self._logger.info(f"App already in list: {path}")
                return True

        self._config.apps.append(TunneledApp(
            name=name,
            path=path,
            enabled=True,
            is_custom=True,
        ))
        self._config.custom_paths.append(path)
        self._save_config()

        self._logger.info(f"Added custom app: {name} ({path})")
        return True

    def remove_custom_app(self, path: str) -> bool:
        """
        Remove a custom app from tunnel list.

        Args:
            path: Path to remove

        Returns:
            True if removed
        """
        self._config.apps = [app for app in self._config.apps if app.path != path]
        if path in self._config.custom_paths:
            self._config.custom_paths.remove(path)
        self._save_config()
        return True

    def set_include_browsers(self, include: bool) -> None:
        """Set whether to include browsers in tunneling."""
        self._config.include_browsers = include
        self._save_config()

    def run_app_through_tunnel(self, app_path: str, args: Optional[list[str]] = None) -> bool:
        """
        Run an application through the tunnel using cgproxy.

        Args:
            app_path: Path to application
            args: Additional arguments

        Returns:
            True if launched successfully
        """
        if not self._check_binary_exists("cgproxy"):
            self._logger.error("cgproxy not installed")
            return False

        cmd = ["cgproxy", app_path]
        if args:
            cmd.extend(args)

        result = self._shell.run(cmd, timeout=5)
        return result.success

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _check_dependencies(self) -> bool:
        """Check required dependencies are installed."""
        # Check for cgproxy
        if not self._check_binary_exists("cgproxy"):
            self._logger.error("cgproxy not installed")
            self._logger.info("Install with: sudo apt install cgproxy")
            self._logger.info("Or from: https://github.com/springzfx/cgproxy")
            return False

        # Check cgroups v2
        if not Path("/sys/fs/cgroup/cgroup.controllers").exists():
            self._logger.error("cgroups v2 not available")
            self._logger.info("Ensure your system uses cgroups v2")
            return False

        return True

    def _build_app_list(self, apps: Optional[list[str]],
                        include_browsers: bool) -> list[TunneledApp]:
        """
        Build list of apps to tunnel.

        Args:
            apps: App names or paths
            include_browsers: Include browser apps

        Returns:
            List of TunneledApp objects
        """
        result = []
        added_paths = set()

        # Add requested apps
        if apps:
            for app in apps:
                # Check if it's a known app name
                if app in KNOWN_APPS:
                    for path in KNOWN_APPS[app]:
                        if Path(path).exists() and path not in added_paths:
                            result.append(TunneledApp(
                                name=app,
                                path=path,
                                enabled=True,
                                is_custom=False,
                            ))
                            added_paths.add(path)
                            break
                # Check if it's a path
                elif Path(app).exists() and app not in added_paths:
                    result.append(TunneledApp(
                        name=Path(app).stem,
                        path=app,
                        enabled=True,
                        is_custom=True,
                    ))
                    added_paths.add(app)

        # Add browsers if requested
        if include_browsers:
            for browser in BROWSER_APPS:
                if browser in KNOWN_APPS:
                    for path in KNOWN_APPS[browser]:
                        if Path(path).exists() and path not in added_paths:
                            result.append(TunneledApp(
                                name=browser,
                                path=path,
                                enabled=True,
                                is_custom=False,
                            ))
                            added_paths.add(path)
                            break

        # Always add Discord if available
        if "discord" not in [app.name for app in result]:
            for path in KNOWN_APPS.get("discord", []):
                if Path(path).exists() and path not in added_paths:
                    result.append(TunneledApp(
                        name="discord",
                        path=path,
                        enabled=True,
                        is_custom=False,
                    ))
                    break

        return result

    def _generate_cgproxy_config(self, apps: list[TunneledApp],
                                  interface: str) -> bool:
        """
        Generate cgproxy configuration file.

        Args:
            apps: List of apps to tunnel
            interface: Network interface to use

        Returns:
            True if generated successfully
        """
        # cgproxy config format
        config = {
            "comment": "Generated by SplitWire-Turkey",
            "port": 0,  # Use nftables for routing
            "program_noproxy": [],
            "program_proxy": [app.path for app in apps if app.enabled],
            "cgroup_noproxy": ["/"],  # Default: no proxy
            "cgroup_proxy": [],
            "enable_gateway": False,
            "enable_dns": True,
            "enable_udp": True,
            "enable_tcp": True,
            "enable_ipv6": True,
            "table": 10007,
            "fwmark": 0x9973,
            "cgroup_root": "/sys/fs/cgroup",
        }

        config_content = json.dumps(config, indent=2)

        # Ensure config directory exists
        result = self._run_privileged(["mkdir", "-p", str(CGPROXY_CONFIG_DIR)])
        if not result.success:
            self._logger.error(f"Failed to create config dir: {result.stderr}")
            return False

        # Write config file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            result = self._run_privileged(["cp", temp_path, str(CGPROXY_CONFIG_FILE)])
            if not result.success:
                self._logger.error(f"Failed to write config: {result.stderr}")
                return False

            result = self._run_privileged(["chmod", "644", str(CGPROXY_CONFIG_FILE)])
            return True

        finally:
            Path(temp_path).unlink(missing_ok=True)


# Convenience functions
_split_tunnel_service: Optional[SplitTunnelService] = None


def get_split_tunnel_service() -> SplitTunnelService:
    """Get the global split tunnel service instance."""
    global _split_tunnel_service
    if _split_tunnel_service is None:
        _split_tunnel_service = SplitTunnelService()
    return _split_tunnel_service


if __name__ == "__main__":
    # Test the split tunnel service
    print("=" * 50)
    print("Split Tunnel Service Test")
    print("=" * 50)

    service = SplitTunnelService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print(f"\nIs installed: {service.is_installed()}")
    print(f"Status: {service.status().value}")

    print("\nKnown apps:")
    for app_name in list(KNOWN_APPS.keys())[:5]:
        print(f"  {app_name}")
    print("  ...")

    print("\nAvailable apps on this system:")
    available = service.get_available_apps()
    for app in available[:5]:
        print(f"  {app.name}: {app.path}")
    if len(available) > 5:
        print(f"  ... and {len(available) - 5} more")

    print("\nBrowser apps:", BROWSER_APPS)

    print("\nTest completed!")
