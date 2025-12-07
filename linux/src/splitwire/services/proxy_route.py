"""
App-based proxy routing for SplitWire-Turkey Linux.

Routes specific applications through a SOCKS5 proxy (e.g., ByeDPI).
Uses cgproxy or redsocks for transparent proxying.

This is the Linux equivalent of ProxiFyre on Windows.
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from splitwire.core import get_logger, get_shell
from splitwire.services.base import BaseService, ServiceStatus, ServiceType
from splitwire.services.split_tunnel import KNOWN_APPS, BROWSER_APPS


# ============================================================================
# Constants
# ============================================================================

# Redsocks configuration
REDSOCKS_CONFIG_DIR = Path("/etc/redsocks")
REDSOCKS_CONFIG_FILE = REDSOCKS_CONFIG_DIR / "redsocks.conf"
REDSOCKS_SERVICE = "redsocks.service"

# Local configuration
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire"
PROXY_ROUTE_CONFIG_FILE = LOCAL_CONFIG_DIR / "proxy_route.json"

# iptables chain name
IPTABLES_CHAIN = "SPLITWIRE_PROXY"

# Default proxy settings
DEFAULT_PROXY_HOST = "127.0.0.1"
DEFAULT_PROXY_PORT = 1080


class ProxyMethod(Enum):
    """Method for routing apps through proxy."""
    CGPROXY = "cgproxy"      # cgroup-based (recommended)
    REDSOCKS = "redsocks"    # iptables-based redirect
    ENV = "env"              # Environment variables (per-app only)


@dataclass
class ProxiedApp:
    """Information about an app configured for proxy routing."""
    name: str
    path: str
    enabled: bool = True
    is_custom: bool = False


@dataclass
class ProxyRouteConfig:
    """Proxy routing configuration."""
    enabled: bool = False
    method: ProxyMethod = ProxyMethod.CGPROXY
    proxy_host: str = DEFAULT_PROXY_HOST
    proxy_port: int = DEFAULT_PROXY_PORT
    include_browsers: bool = False
    apps: list[ProxiedApp] = field(default_factory=list)
    custom_paths: list[str] = field(default_factory=list)


class ProxyRouteService(BaseService):
    """
    App-based proxy routing service.

    Routes specific applications through a SOCKS5 proxy using either:
    - cgproxy: cgroup-based routing (clean, recommended)
    - redsocks: iptables-based transparent proxy redirect

    Features:
    - Route specific apps through proxy
    - Predefined app list (Discord, browsers, etc.)
    - Custom app path support
    - Include/exclude browsers option
    """

    def __init__(self):
        """Initialize proxy route service."""
        super().__init__(
            name="proxy-route",
            display_name="Proxy Routing",
            description="App-based proxy routing for ByeDPI",
            service_type=ServiceType.SYSTEM,
        )
        self._config = ProxyRouteConfig()
        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from file."""
        if PROXY_ROUTE_CONFIG_FILE.exists():
            try:
                data = json.loads(PROXY_ROUTE_CONFIG_FILE.read_text())
                self._config = ProxyRouteConfig(
                    enabled=data.get("enabled", False),
                    method=ProxyMethod(data.get("method", "cgproxy")),
                    proxy_host=data.get("proxy_host", DEFAULT_PROXY_HOST),
                    proxy_port=data.get("proxy_port", DEFAULT_PROXY_PORT),
                    include_browsers=data.get("include_browsers", False),
                    custom_paths=data.get("custom_paths", []),
                )
                for app_data in data.get("apps", []):
                    self._config.apps.append(ProxiedApp(
                        name=app_data.get("name", ""),
                        path=app_data.get("path", ""),
                        enabled=app_data.get("enabled", True),
                        is_custom=app_data.get("is_custom", False),
                    ))
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        data = {
            "enabled": self._config.enabled,
            "method": self._config.method.value,
            "proxy_host": self._config.proxy_host,
            "proxy_port": self._config.proxy_port,
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
        PROXY_ROUTE_CONFIG_FILE.write_text(json.dumps(data, indent=2))

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, apps: Optional[list[str]] = None,
                include_browsers: bool = False,
                proxy_host: str = DEFAULT_PROXY_HOST,
                proxy_port: int = DEFAULT_PROXY_PORT,
                method: ProxyMethod = ProxyMethod.CGPROXY,
                **kwargs) -> bool:
        """
        Install and configure proxy routing.

        Args:
            apps: List of app names or paths to route
            include_browsers: Include common browsers
            proxy_host: SOCKS5 proxy host
            proxy_port: SOCKS5 proxy port
            method: Routing method (cgproxy or redsocks)

        Returns:
            True if installation successful
        """
        self._logger.info(f"Installing proxy routing via {method.value}")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Check dependencies
            if not self._check_dependencies(method):
                return False

            # Update config
            self._config.proxy_host = proxy_host
            self._config.proxy_port = proxy_port
            self._config.method = method
            self._config.include_browsers = include_browsers

            # Build app list
            proxy_apps = self._build_app_list(apps, include_browsers)
            if not proxy_apps:
                self._logger.warning("No apps to route")
                return False

            self._config.apps = proxy_apps

            # Setup routing based on method
            if method == ProxyMethod.CGPROXY:
                if not self._setup_cgproxy(proxy_apps):
                    return False
            elif method == ProxyMethod.REDSOCKS:
                if not self._setup_redsocks(proxy_apps):
                    return False

            self._config.enabled = True
            self._save_config()

            self._logger.info("Proxy routing installed successfully")
            return True

        except Exception as e:
            self._logger.exception(f"Installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """Remove proxy routing configuration."""
        self._logger.info("Removing proxy routing")

        try:
            if self.is_running():
                self.stop()

            # Cleanup based on method
            if self._config.method == ProxyMethod.CGPROXY:
                self._cleanup_cgproxy()
            elif self._config.method == ProxyMethod.REDSOCKS:
                self._cleanup_redsocks()

            self._config.enabled = False
            self._save_config()

            self._logger.info("Proxy routing removed")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.exception(f"Removal failed: {e}")
            return False

    def start(self) -> bool:
        """Start proxy routing."""
        self._logger.info("Starting proxy routing")

        if self._config.method == ProxyMethod.REDSOCKS:
            # Start redsocks service
            result = self._run_privileged(
                ["systemctl", "start", REDSOCKS_SERVICE],
                timeout=30
            )
            if result.success:
                # Add iptables rules
                self._add_iptables_rules()
            else:
                self._logger.error(f"Failed to start redsocks: {result.stderr}")
                return False

        self._notify_status_change(ServiceStatus.RUNNING)
        return True

    def stop(self) -> bool:
        """Stop proxy routing."""
        self._logger.info("Stopping proxy routing")

        if self._config.method == ProxyMethod.REDSOCKS:
            # Remove iptables rules
            self._remove_iptables_rules()

            # Stop redsocks service
            self._run_privileged(
                ["systemctl", "stop", REDSOCKS_SERVICE],
                timeout=30
            )

        self._notify_status_change(ServiceStatus.STOPPED)
        return True

    def status(self) -> ServiceStatus:
        """Get proxy routing status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        if self._config.method == ProxyMethod.REDSOCKS:
            result = self._shell.run(
                ["systemctl", "is-active", REDSOCKS_SERVICE],
                timeout=10
            )
            if result.stdout.strip().lower() == "active":
                return ServiceStatus.RUNNING
            return ServiceStatus.STOPPED

        # For cgproxy, check if configured
        if self._config.enabled:
            return ServiceStatus.RUNNING

        return ServiceStatus.STOPPED

    def is_installed(self) -> bool:
        """Check if proxy routing is configured."""
        return self._config.enabled

    # =========================================================================
    # Proxy route specific methods
    # =========================================================================

    def get_config(self) -> ProxyRouteConfig:
        """Get current configuration."""
        return self._config

    def get_available_apps(self) -> list[ProxiedApp]:
        """Get list of apps available for proxy routing."""
        available = []
        for app_name, paths in KNOWN_APPS.items():
            for path in paths:
                if Path(path).exists():
                    available.append(ProxiedApp(
                        name=app_name,
                        path=path,
                        enabled=False,
                        is_custom=False,
                    ))
                    break
        return available

    def get_proxied_apps(self) -> list[ProxiedApp]:
        """Get list of currently proxied apps."""
        return [app for app in self._config.apps if app.enabled]

    def add_custom_app(self, name: str, path: str) -> bool:
        """Add a custom app to proxy list."""
        if not Path(path).exists():
            self._logger.error(f"Path does not exist: {path}")
            return False

        for app in self._config.apps:
            if app.path == path:
                self._logger.info(f"App already in list: {path}")
                return True

        self._config.apps.append(ProxiedApp(
            name=name,
            path=path,
            enabled=True,
            is_custom=True,
        ))
        self._config.custom_paths.append(path)
        self._save_config()
        return True

    def remove_custom_app(self, path: str) -> bool:
        """Remove a custom app from proxy list."""
        self._config.apps = [app for app in self._config.apps if app.path != path]
        if path in self._config.custom_paths:
            self._config.custom_paths.remove(path)
        self._save_config()
        return True

    def set_proxy(self, host: str, port: int) -> None:
        """Set proxy server address."""
        self._config.proxy_host = host
        self._config.proxy_port = port
        self._save_config()

    def configure(self, apps: Optional[list[str]] = None,
                  include_browsers: bool = False,
                  proxy_host: Optional[str] = None,
                  proxy_port: Optional[int] = None) -> bool:
        """
        Configure proxy routing (wrapper for install).

        Args:
            apps: List of app names or paths to route
            include_browsers: Include common browsers
            proxy_host: SOCKS5 proxy host
            proxy_port: SOCKS5 proxy port

        Returns:
            True if configuration successful
        """
        return self.install(
            apps=apps,
            include_browsers=include_browsers,
            proxy_host=proxy_host or self._config.proxy_host,
            proxy_port=proxy_port or self._config.proxy_port,
            method=self._config.method
        )

    def run_app_through_proxy(self, app_path: str, args: Optional[list[str]] = None) -> bool:
        """
        Run an application through the proxy.

        Args:
            app_path: Path to application
            args: Additional arguments

        Returns:
            True if launched successfully
        """
        if self._config.method == ProxyMethod.CGPROXY:
            return self._run_via_cgproxy(app_path, args)
        elif self._config.method == ProxyMethod.ENV:
            return self._run_via_env(app_path, args)
        else:
            self._logger.warning("Run through proxy only supported for cgproxy/env")
            return False

    # =========================================================================
    # cgproxy methods
    # =========================================================================

    def _setup_cgproxy(self, apps: list[ProxiedApp]) -> bool:
        """Setup cgproxy for SOCKS5 proxy routing."""
        # cgproxy config for SOCKS proxy
        config = {
            "comment": "Generated by SplitWire-Turkey for ByeDPI",
            "port": self._config.proxy_port,
            "socks5": f"{self._config.proxy_host}:{self._config.proxy_port}",
            "program_noproxy": [],
            "program_proxy": [app.path for app in apps if app.enabled],
            "cgroup_noproxy": ["/"],
            "cgroup_proxy": [],
            "enable_gateway": False,
            "enable_dns": True,
            "enable_udp": True,
            "enable_tcp": True,
            "enable_ipv6": True,
            "table": 10008,
            "fwmark": 0x9974,
            "cgroup_root": "/sys/fs/cgroup",
        }

        config_content = json.dumps(config, indent=2)
        cgproxy_config = Path("/etc/cgproxy/config.json")

        try:
            # Create config directory
            result = self._run_privileged(["mkdir", "-p", "/etc/cgproxy"])
            if not result.success:
                return False

            # Write config
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(config_content)
                tmp_path = f.name

            result = self._run_privileged(["cp", tmp_path, str(cgproxy_config)])
            Path(tmp_path).unlink(missing_ok=True)

            if not result.success:
                return False

            self._logger.info("cgproxy configured for SOCKS5 proxy")
            return True

        except Exception as e:
            self._logger.exception(f"Failed to setup cgproxy: {e}")
            return False

    def _cleanup_cgproxy(self) -> None:
        """Remove cgproxy configuration."""
        self._run_privileged(["rm", "-f", "/etc/cgproxy/config.json"])

    def _run_via_cgproxy(self, app_path: str, args: Optional[list[str]] = None) -> bool:
        """Run app through cgproxy."""
        if not self._shell.command_exists("cgproxy"):
            self._logger.error("cgproxy not installed")
            return False

        cmd = ["cgproxy", app_path]
        if args:
            cmd.extend(args)

        result = self._shell.run(cmd, timeout=5)
        return result.success

    # =========================================================================
    # redsocks methods
    # =========================================================================

    def _setup_redsocks(self, apps: list[ProxiedApp]) -> bool:
        """Setup redsocks for transparent proxying."""
        config_content = f"""base {{
    log_debug = off;
    log_info = on;
    log = "syslog:daemon";
    daemon = on;
    redirector = iptables;
}}

redsocks {{
    local_ip = 127.0.0.1;
    local_port = 12345;
    ip = {self._config.proxy_host};
    port = {self._config.proxy_port};
    type = socks5;
}}
"""

        try:
            # Create config directory
            result = self._run_privileged(["mkdir", "-p", str(REDSOCKS_CONFIG_DIR)])
            if not result.success:
                return False

            # Write config
            with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
                f.write(config_content)
                tmp_path = f.name

            result = self._run_privileged(["cp", tmp_path, str(REDSOCKS_CONFIG_FILE)])
            Path(tmp_path).unlink(missing_ok=True)

            if not result.success:
                return False

            self._logger.info("redsocks configured")
            return True

        except Exception as e:
            self._logger.exception(f"Failed to setup redsocks: {e}")
            return False

    def _cleanup_redsocks(self) -> None:
        """Remove redsocks configuration."""
        self._remove_iptables_rules()
        self._run_privileged(["rm", "-f", str(REDSOCKS_CONFIG_FILE)])

    def _add_iptables_rules(self) -> None:
        """Add iptables rules for redsocks."""
        commands = [
            # Create chain
            f"iptables -t nat -N {IPTABLES_CHAIN}",
            # Skip local addresses
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 0.0.0.0/8 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 10.0.0.0/8 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 127.0.0.0/8 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 169.254.0.0/16 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 172.16.0.0/12 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 192.168.0.0/16 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 224.0.0.0/4 -j RETURN",
            f"iptables -t nat -A {IPTABLES_CHAIN} -d 240.0.0.0/4 -j RETURN",
            # Redirect to redsocks
            f"iptables -t nat -A {IPTABLES_CHAIN} -p tcp -j REDIRECT --to-ports 12345",
            # Apply to OUTPUT
            f"iptables -t nat -A OUTPUT -p tcp -j {IPTABLES_CHAIN}",
        ]

        for cmd in commands:
            self._run_privileged(cmd.split())

    def _remove_iptables_rules(self) -> None:
        """Remove iptables rules."""
        commands = [
            f"iptables -t nat -D OUTPUT -p tcp -j {IPTABLES_CHAIN}",
            f"iptables -t nat -F {IPTABLES_CHAIN}",
            f"iptables -t nat -X {IPTABLES_CHAIN}",
        ]

        for cmd in commands:
            self._run_privileged(cmd.split())

    # =========================================================================
    # Environment variable method
    # =========================================================================

    def _run_via_env(self, app_path: str, args: Optional[list[str]] = None) -> bool:
        """Run app with proxy environment variables."""
        proxy_url = f"socks5://{self._config.proxy_host}:{self._config.proxy_port}"

        env = {
            **dict(subprocess.os.environ),
            "http_proxy": proxy_url,
            "https_proxy": proxy_url,
            "HTTP_PROXY": proxy_url,
            "HTTPS_PROXY": proxy_url,
            "all_proxy": proxy_url,
            "ALL_PROXY": proxy_url,
        }

        cmd = [app_path]
        if args:
            cmd.extend(args)

        try:
            subprocess.Popen(cmd, env=env, start_new_session=True)
            return True
        except Exception as e:
            self._logger.error(f"Failed to run app: {e}")
            return False

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _check_dependencies(self, method: ProxyMethod) -> bool:
        """Check required dependencies."""
        if method == ProxyMethod.CGPROXY:
            if not self._shell.command_exists("cgproxy"):
                self._logger.error("cgproxy not installed")
                self._logger.info("Install from: https://github.com/springzfx/cgproxy")
                return False

            if not Path("/sys/fs/cgroup/cgroup.controllers").exists():
                self._logger.error("cgroups v2 not available")
                return False

        elif method == ProxyMethod.REDSOCKS:
            if not self._shell.command_exists("redsocks"):
                self._logger.error("redsocks not installed")
                self._logger.info("Install with: sudo apt install redsocks")
                return False

        return True

    def _build_app_list(self, apps: Optional[list[str]],
                        include_browsers: bool) -> list[ProxiedApp]:
        """Build list of apps to route through proxy."""
        result = []
        added_paths = set()

        # Add requested apps
        if apps:
            for app in apps:
                if app in KNOWN_APPS:
                    for path in KNOWN_APPS[app]:
                        if Path(path).exists() and path not in added_paths:
                            result.append(ProxiedApp(
                                name=app,
                                path=path,
                                enabled=True,
                                is_custom=False,
                            ))
                            added_paths.add(path)
                            break
                elif Path(app).exists() and app not in added_paths:
                    result.append(ProxiedApp(
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
                            result.append(ProxiedApp(
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
                    result.append(ProxiedApp(
                        name="discord",
                        path=path,
                        enabled=True,
                        is_custom=False,
                    ))
                    break

        return result


# ============================================================================
# Convenience functions
# ============================================================================

_proxy_route_service: Optional[ProxyRouteService] = None


def get_proxy_route_service() -> ProxyRouteService:
    """Get the global proxy route service instance."""
    global _proxy_route_service
    if _proxy_route_service is None:
        _proxy_route_service = ProxyRouteService()
    return _proxy_route_service


if __name__ == "__main__":
    # Test the proxy route service
    print("=" * 50)
    print("Proxy Route Service Test")
    print("=" * 50)

    service = ProxyRouteService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print(f"\nIs installed: {service.is_installed()}")
    print(f"Status: {service.status().value}")

    config = service.get_config()
    print(f"\nConfig:")
    print(f"  Method: {config.method.value}")
    print(f"  Proxy: {config.proxy_host}:{config.proxy_port}")
    print(f"  Include browsers: {config.include_browsers}")

    print("\nAvailable apps:")
    available = service.get_available_apps()
    for app in available[:5]:
        print(f"  {app.name}: {app.path}")
    if len(available) > 5:
        print(f"  ... and {len(available) - 5} more")

    print("\nProxy methods:", [m.value for m in ProxyMethod])

    print("\nTest completed!")
