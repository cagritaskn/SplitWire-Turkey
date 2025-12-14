"""
WireGuard VPN service for SplitWire-Turkey Linux.

Provides WireGuard VPN management with:
- wg-quick up/down commands
- WGCF integration for Cloudflare WARP
- Config file management
- Interface status monitoring
- IP-based split tunneling via AllowedIPs
"""

import os
import re
import json
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from .base import BaseService, ServiceStatus, ServiceType, ServiceInfo
from splitwire.core import get_logger, get_shell, get_config


# WireGuard configuration paths
WIREGUARD_CONFIG_DIR = Path("/etc/wireguard")
SPLITWIRE_CONFIG_NAME = "splitwire"
SPLITWIRE_CONFIG_FILE = WIREGUARD_CONFIG_DIR / f"{SPLITWIRE_CONFIG_NAME}.conf"

# WGCF binary and account paths
WGCF_BINARY_NAME = "wgcf"
WGCF_GITHUB_REPO = "ViRb3/wgcf"
WGCF_GITHUB_API = f"https://api.github.com/repos/{WGCF_GITHUB_REPO}/releases/latest"

# Local paths
LOCAL_DATA_DIR = Path.home() / ".local" / "share" / "splitwire"
WGCF_DIR = LOCAL_DATA_DIR / "wgcf"
WGCF_BINARY = WGCF_DIR / WGCF_BINARY_NAME
WGCF_ACCOUNT_FILE = WGCF_DIR / "wgcf-account.toml"
WGCF_PROFILE_FILE = WGCF_DIR / "wgcf-profile.conf"

# Default excluded networks (local/private)
DEFAULT_EXCLUDED_NETWORKS = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "224.0.0.0/4",
    "255.255.255.255/32",
]


@dataclass
class WireGuardInterface:
    """Information about a WireGuard interface."""
    name: str
    public_key: str = ""
    private_key: str = ""
    address: str = ""
    listen_port: int = 0
    endpoint: str = ""
    latest_handshake: str = ""
    transfer_rx: int = 0
    transfer_tx: int = 0
    allowed_ips: list[str] = field(default_factory=list)


@dataclass
class WGCFAccount:
    """WGCF account information."""
    device_id: str = ""
    access_token: str = ""
    private_key: str = ""
    license_key: str = ""
    created: str = ""


class WireGuardService(BaseService):
    """
    WireGuard VPN service manager.

    Features:
    - Install/remove WireGuard configuration
    - Start/stop VPN connection via wg-quick
    - WGCF integration for Cloudflare WARP
    - IP-based split tunneling
    - Interface status monitoring
    """

    def __init__(self):
        """Initialize WireGuard service."""
        super().__init__(
            name="wireguard",
            display_name="WireGuard VPN",
            description="WireGuard VPN with Cloudflare WARP",
            service_type=ServiceType.VPN,
        )
        self._interface_name = SPLITWIRE_CONFIG_NAME
        self._config_file = SPLITWIRE_CONFIG_FILE
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        WGCF_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, allowed_apps: Optional[list[str]] = None,
                include_browsers: bool = False,
                use_warp: bool = True,
                custom_config: Optional[Path] = None,
                **kwargs) -> bool:
        """
        Install WireGuard VPN configuration.

        Args:
            allowed_apps: List of app paths to tunnel (for cgproxy)
            include_browsers: Include browsers in tunneling
            use_warp: Use Cloudflare WARP via wgcf
            custom_config: Path to custom WireGuard config

        Returns:
            True if installation successful
        """
        self._logger.info("Installing WireGuard VPN")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Check dependencies
            if not self._check_dependencies():
                return False

            # Get or generate config
            if custom_config and custom_config.exists():
                config_content = custom_config.read_text()
            elif use_warp:
                config_content = self._generate_warp_config()
                if not config_content:
                    self._logger.error("Failed to generate WARP config")
                    return False
            else:
                self._logger.error("No config source specified")
                return False

            # Modify config for split tunneling if needed
            if allowed_apps:
                # Store app list for cgproxy (handled by split_tunnel module)
                config = get_config()
                config.wireguard.allowed_apps = allowed_apps

            # Install config file
            if not self._install_config(config_content):
                return False

            # Start the VPN
            if not self.start():
                return False

            self._logger.info("WireGuard VPN installed successfully")
            return True

        except Exception as e:
            self._logger.exception(f"Installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """Remove WireGuard VPN configuration."""
        self._logger.info("Removing WireGuard VPN")

        try:
            # Stop if running
            if self.is_running():
                self.stop()

            # Remove config file
            if self._check_config_exists():
                result = self._run_privileged(["rm", "-f", str(self._config_file)])
                if not result.success:
                    self._logger.warning(f"Failed to remove config: {result.stderr}")

            self._logger.info("WireGuard VPN removed")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.exception(f"Removal failed: {e}")
            return False

    def start(self) -> bool:
        """Start WireGuard VPN connection."""
        self._logger.info("Starting WireGuard VPN")

        # Check if already running
        if self.is_running():
            self._logger.info("WireGuard VPN already running")
            return True

        # Check config file exists (use shell to avoid permission issues)
        if not self._check_config_exists():
            self._logger.error("Config file not found")
            return False

        result = self._run_privileged(
            ["wg-quick", "up", self._interface_name],
            timeout=30
        )

        if result.success:
            self._logger.info("WireGuard VPN started")
            self._notify_status_change(ServiceStatus.RUNNING)
            return True
        else:
            self._logger.error(f"Failed to start: {result.stderr}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def stop(self) -> bool:
        """Stop WireGuard VPN connection."""
        self._logger.info("Stopping WireGuard VPN")

        result = self._run_privileged(
            ["wg-quick", "down", self._interface_name],
            timeout=30
        )

        if result.success:
            self._logger.info("WireGuard VPN stopped")
            self._notify_status_change(ServiceStatus.STOPPED)
            return True
        else:
            # wg-quick returns error if interface doesn't exist
            if "is not a WireGuard interface" in result.stderr:
                self._notify_status_change(ServiceStatus.STOPPED)
                return True
            self._logger.error(f"Failed to stop: {result.stderr}")
            return False

    def status(self) -> ServiceStatus:
        """Get WireGuard VPN status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        # Check if interface exists
        result = self._shell.run(["ip", "link", "show", self._interface_name])
        if result.success:
            return ServiceStatus.RUNNING
        else:
            return ServiceStatus.STOPPED

    def _check_config_exists(self) -> bool:
        """Check if config file exists (handles permission issues)."""
        try:
            return self._config_file.exists()
        except PermissionError:
            # Can't check directly, try via shell with sudo
            result = self._shell.run(
                ["sudo", "test", "-f", str(self._config_file)],
                timeout=5
            )
            return result.success

    def is_installed(self) -> bool:
        """Check if WireGuard config is installed."""
        return self._check_config_exists()

    def get_info(self) -> ServiceInfo:
        """Get comprehensive service information."""
        info = super().get_info()

        if self.is_running():
            interface = self.get_interface_info()
            if interface:
                info.metadata = {
                    "public_key": interface.public_key,
                    "endpoint": interface.endpoint,
                    "latest_handshake": interface.latest_handshake,
                    "transfer_rx": interface.transfer_rx,
                    "transfer_tx": interface.transfer_tx,
                }

        info.config_path = self._config_file
        return info

    # =========================================================================
    # WireGuard specific methods
    # =========================================================================

    def get_interface_info(self) -> Optional[WireGuardInterface]:
        """
        Get information about the WireGuard interface.

        Returns:
            WireGuardInterface with current state or None
        """
        if not self.is_running():
            return None

        result = self._run_privileged(["wg", "show", self._interface_name])
        if not result.success:
            return None

        return self._parse_wg_show(result.stdout)

    def test_connection(self, test_host: str = "1.1.1.1") -> bool:
        """
        Test VPN connection by pinging through the tunnel.

        Args:
            test_host: Host to ping

        Returns:
            True if connection is working
        """
        if not self.is_running():
            return False

        result = self._shell.run(
            ["ping", "-c", "1", "-W", "5", "-I", self._interface_name, test_host],
            timeout=10
        )
        return result.success

    def get_transfer_stats(self) -> tuple[int, int]:
        """
        Get transfer statistics.

        Returns:
            Tuple of (bytes_received, bytes_sent)
        """
        interface = self.get_interface_info()
        if interface:
            return (interface.transfer_rx, interface.transfer_tx)
        return (0, 0)

    # =========================================================================
    # WGCF Integration
    # =========================================================================

    def ensure_wgcf(self) -> bool:
        """
        Ensure wgcf binary is available.

        Downloads from GitHub if not present.

        Returns:
            True if wgcf is available
        """
        if WGCF_BINARY.exists() and os.access(WGCF_BINARY, os.X_OK):
            return True

        self._logger.info("Downloading wgcf...")
        return self._download_wgcf()

    def register_warp_account(self) -> bool:
        """
        Register a new Cloudflare WARP account using wgcf.

        Returns:
            True if registration successful
        """
        if not self.ensure_wgcf():
            return False

        # Check if account already exists
        if WGCF_ACCOUNT_FILE.exists():
            self._logger.info("WARP account already exists")
            return True

        self._logger.info("Registering WARP account...")

        result = self._shell.run(
            [str(WGCF_BINARY), "register", "--accept-tos"],
            cwd=WGCF_DIR,
            timeout=60
        )

        if result.success:
            self._logger.info("WARP account registered")
            return True
        else:
            self._logger.error(f"Registration failed: {result.stderr}")
            return False

    def generate_warp_profile(self) -> bool:
        """
        Generate WireGuard profile from WARP account.

        Returns:
            True if generation successful
        """
        if not WGCF_ACCOUNT_FILE.exists():
            if not self.register_warp_account():
                return False

        self._logger.info("Generating WARP profile...")

        result = self._shell.run(
            [str(WGCF_BINARY), "generate"],
            cwd=WGCF_DIR,
            timeout=60
        )

        if result.success and WGCF_PROFILE_FILE.exists():
            self._logger.info("WARP profile generated")
            return True
        else:
            self._logger.error(f"Profile generation failed: {result.stderr}")
            return False

    def _generate_warp_config(self) -> Optional[str]:
        """
        Generate WireGuard config for WARP.

        Returns:
            Config content or None
        """
        # Ensure profile exists
        if not WGCF_PROFILE_FILE.exists():
            if not self.generate_warp_profile():
                return None

        # Read and modify profile
        config = WGCF_PROFILE_FILE.read_text()

        # Modify AllowedIPs to exclude local networks (split tunnel)
        config = self._modify_allowed_ips(config)

        # Add custom DNS
        config = self._add_dns_config(config)

        return config

    def _modify_allowed_ips(self, config: str,
                            excluded: Optional[list[str]] = None) -> str:
        """
        Modify AllowedIPs in config for split tunneling.

        By default, routes all traffic except local networks.

        Args:
            config: Original config content
            excluded: Networks to exclude from VPN

        Returns:
            Modified config
        """
        excluded = excluded or DEFAULT_EXCLUDED_NETWORKS

        # Use Cloudflare WARP IPs instead of routing all traffic
        # This prevents complete internet outage if VPN fails
        # WARP typically uses these ranges for its services
        allowed_ips = ", ".join([
            "162.159.192.0/24",  # Cloudflare WARP
            "162.159.193.0/24",  # Cloudflare WARP
            "162.159.195.0/24",  # Cloudflare WARP
            "162.159.204.0/24",  # Cloudflare WARP
            "188.114.96.0/24",   # Cloudflare
            "188.114.97.0/24",   # Cloudflare
            "104.16.0.0/12",     # Cloudflare CDN (Discord, etc.)
            "172.64.0.0/13",     # Cloudflare
        ])

        # Replace existing AllowedIPs
        config = re.sub(
            r'^AllowedIPs\s*=.*$',
            f'AllowedIPs = {allowed_ips}',
            config,
            flags=re.MULTILINE
        )

        return config

    def _add_dns_config(self, config: str) -> str:
        """
        Add DNS configuration to WireGuard config.

        Args:
            config: Original config content

        Returns:
            Modified config with DNS
        """
        # Check if DNS already configured
        if re.search(r'^DNS\s*=', config, re.MULTILINE):
            return config

        # Add DNS after Address line
        dns_line = "DNS = 1.1.1.1, 1.0.0.1"
        config = re.sub(
            r'^(Address\s*=.*)$',
            f'\\1\n{dns_line}',
            config,
            flags=re.MULTILINE
        )

        return config

    def _download_wgcf(self) -> bool:
        """
        Download wgcf binary from GitHub.

        Returns:
            True if download successful
        """
        try:
            # Get latest release info
            self._logger.debug("Fetching wgcf release info...")
            req = Request(WGCF_GITHUB_API)
            req.add_header("User-Agent", "SplitWire-Turkey")

            with urlopen(req, timeout=30) as response:
                release_info = json.loads(response.read().decode())

            # Find Linux amd64 asset
            download_url = None
            for asset in release_info.get("assets", []):
                name = asset.get("name", "")
                if "linux" in name.lower() and "amd64" in name.lower():
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                self._logger.error("Could not find wgcf Linux amd64 binary")
                return False

            # Download binary
            self._logger.info(f"Downloading from {download_url}")
            req = Request(download_url)
            req.add_header("User-Agent", "SplitWire-Turkey")

            with urlopen(req, timeout=120) as response:
                binary_data = response.read()

            # Save binary
            WGCF_BINARY.write_bytes(binary_data)
            os.chmod(WGCF_BINARY, 0o755)

            self._logger.info("wgcf downloaded successfully")
            return True

        except (URLError, HTTPError) as e:
            self._logger.error(f"Download failed: {e}")
            return False
        except Exception as e:
            self._logger.exception(f"Download error: {e}")
            return False

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _check_dependencies(self) -> bool:
        """Check required dependencies are installed."""
        required = ["wg", "wg-quick", "ip"]
        missing = []

        for cmd in required:
            if not self._check_binary_exists(cmd):
                missing.append(cmd)

        if missing:
            self._logger.error(f"Missing dependencies: {', '.join(missing)}")
            self._logger.info("Install with: sudo apt install wireguard-tools")
            return False

        return True

    def _install_config(self, config_content: str) -> bool:
        """
        Install WireGuard config file.

        Args:
            config_content: Config file content

        Returns:
            True if installation successful
        """
        # Ensure /etc/wireguard exists
        result = self._run_privileged(
            ["mkdir", "-p", str(WIREGUARD_CONFIG_DIR)]
        )
        if not result.success:
            self._logger.error(f"Failed to create config dir: {result.stderr}")
            return False

        # Write config to temp file first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            # Copy to /etc/wireguard with correct permissions
            result = self._run_privileged(
                ["cp", temp_path, str(self._config_file)]
            )
            if not result.success:
                self._logger.error(f"Failed to copy config: {result.stderr}")
                return False

            # Set permissions (600 - owner read/write only)
            result = self._run_privileged(
                ["chmod", "600", str(self._config_file)]
            )
            if not result.success:
                self._logger.warning(f"Failed to set permissions: {result.stderr}")

            return True

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

    def _parse_wg_show(self, output: str) -> WireGuardInterface:
        """
        Parse output of 'wg show' command.

        Args:
            output: Command output

        Returns:
            WireGuardInterface with parsed data
        """
        interface = WireGuardInterface(name=self._interface_name)

        for line in output.splitlines():
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "public key":
                    interface.public_key = value
                elif key == "private key":
                    interface.private_key = value
                elif key == "listening port":
                    interface.listen_port = int(value) if value.isdigit() else 0
                elif key == "endpoint":
                    interface.endpoint = value
                elif key == "allowed ips":
                    interface.allowed_ips = [ip.strip() for ip in value.split(",")]
                elif key == "latest handshake":
                    interface.latest_handshake = value
                elif key == "transfer":
                    # Parse "X MiB received, Y MiB sent"
                    match = re.search(r'([\d.]+)\s*\w+\s*received.*?([\d.]+)\s*\w+\s*sent', value)
                    if match:
                        # Convert to bytes (approximate)
                        interface.transfer_rx = int(float(match.group(1)) * 1024 * 1024)
                        interface.transfer_tx = int(float(match.group(2)) * 1024 * 1024)

        return interface

    # =========================================================================
    # Stub methods for UI compatibility
    # =========================================================================

    def register_wgcf(self) -> bool:
        """
        Register WGCF/WARP account.
        Alias for register_warp_account() for UI compatibility.
        """
        return self.register_warp_account()

    def enable_refresh_timer(self) -> bool:
        """
        Enable connection refresh timer.
        Note: Not fully implemented for Linux yet.
        """
        self._logger.info("Refresh timer enabled (stub)")
        # TODO: Implement systemd timer for connection refresh
        return True

    def disable_refresh_timer(self) -> bool:
        """
        Disable connection refresh timer.
        Note: Not fully implemented for Linux yet.
        """
        self._logger.info("Refresh timer disabled (stub)")
        return True

    def generate_config(self, allowed_apps: Optional[list[str]] = None,
                       include_browsers: bool = False,
                       endpoint: Optional[str] = None) -> Optional[str]:
        """
        Generate WireGuard configuration and install it.

        Args:
            allowed_apps: List of apps to tunnel
            include_browsers: Include browser apps
            endpoint: Endpoint type (e.g., "alternative" for alternate servers)

        Returns:
            Path to generated config file or None
        """
        self._logger.info(f"Generating WireGuard config (endpoint={endpoint})...")

        # Generate WARP profile
        if not self.generate_warp_profile():
            return None

        # Read the generated profile
        try:
            config_content = WGCF_PROFILE_FILE.read_text()

            # Modify config
            config_content = self._modify_allowed_ips(config_content)
            config_content = self._add_dns_config(config_content)

            # Install to /etc/wireguard/
            if self._install_config(config_content):
                return str(self._config_file)
            else:
                self._logger.error("Failed to install config")
                return None

        except Exception as e:
            self._logger.error(f"Failed to generate config: {e}")
            return None

    def generate_config_content(self, allowed_apps: Optional[list[str]] = None,
                                include_browsers: bool = False) -> str:
        """
        Generate WireGuard configuration content as string.

        Args:
            allowed_apps: List of apps to tunnel
            include_browsers: Include browser apps

        Returns:
            Configuration file content as string
        """
        self._logger.info("Generating WireGuard config content...")

        # Ensure profile exists
        if not WGCF_PROFILE_FILE.exists():
            if not self.generate_warp_profile():
                return ""

        # Read and return the config
        try:
            config = WGCF_PROFILE_FILE.read_text()
            # Apply modifications
            config = self._modify_allowed_ips(config)
            config = self._add_dns_config(config)
            return config
        except Exception as e:
            self._logger.error(f"Failed to read config: {e}")
            return ""


# Convenience functions
_wireguard_service: Optional[WireGuardService] = None


def get_wireguard_service() -> WireGuardService:
    """Get the global WireGuard service instance."""
    global _wireguard_service
    if _wireguard_service is None:
        _wireguard_service = WireGuardService()
    return _wireguard_service


if __name__ == "__main__":
    # Test the WireGuard service
    print("=" * 50)
    print("WireGuard Service Test")
    print("=" * 50)

    service = WireGuardService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print(f"\nIs installed: {service.is_installed()}")
    print(f"Status: {service.status().value}")

    print("\nChecking dependencies...")
    deps = ["wg", "wg-quick", "ip"]
    for dep in deps:
        exists = service._check_binary_exists(dep)
        print(f"  {dep}: {'OK' if exists else 'MISSING'}")

    print("\nWGCF paths:")
    print(f"  Binary: {WGCF_BINARY}")
    print(f"  Account: {WGCF_ACCOUNT_FILE}")
    print(f"  Profile: {WGCF_PROFILE_FILE}")

    if service.is_running():
        print("\nInterface info:")
        info = service.get_interface_info()
        if info:
            print(f"  Public key: {info.public_key[:20]}...")
            print(f"  Endpoint: {info.endpoint}")
            print(f"  Handshake: {info.latest_handshake}")

    print("\nTest completed!")
