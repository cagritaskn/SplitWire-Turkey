"""
ByeDPI (ciadpi) proxy service for SplitWire-Turkey Linux.

Provides SOCKS5 proxy with DPI bypass capabilities.
ciadpi is the Linux version of ByeDPI.
"""

import json
import os
import signal
import stat
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Callable
import urllib.request
import platform

from splitwire.core import get_logger, get_shell
from splitwire.services.base import BaseService, ServiceStatus, ServiceType


# ============================================================================
# Constants
# ============================================================================

# Installation paths
BYEDPI_INSTALL_DIR = Path("/opt/byedpi")
BYEDPI_BINARY = BYEDPI_INSTALL_DIR / "ciadpi"
BYEDPI_CONFIG_DIR = BYEDPI_INSTALL_DIR / "config"

# Local config
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire" / "byedpi"
PRESETS_FILE = LOCAL_CONFIG_DIR / "presets.json"
CONFIG_FILE = LOCAL_CONFIG_DIR / "config.json"

# PID file for process tracking
PID_DIR = Path("/run/splitwire")
BYEDPI_PID_FILE = PID_DIR / "ciadpi.pid"

# GitHub releases
CIADPI_REPO = "hufrea/byedpi"
CIADPI_RELEASE_URL = f"https://api.github.com/repos/{CIADPI_REPO}/releases/latest"

# Default proxy settings
DEFAULT_PROXY_HOST = "127.0.0.1"
DEFAULT_PROXY_PORT = 1080

# systemd service name
SYSTEMD_SERVICE = "splitwire-byedpi.service"


class ByeDPIMode(Enum):
    """ByeDPI operation mode."""
    DISORDER = "disorder"      # Packet reordering
    SPLIT = "split"            # Packet splitting
    FAKE = "fake"              # Fake packets
    OOB = "oob"                # Out-of-band data
    DISOOB = "disoob"          # Disorder + OOB
    COMBINED = "combined"      # Multiple methods


@dataclass
class ByeDPIPreset:
    """Configuration preset for ByeDPI."""
    name: str
    description: str
    args: str
    mode: ByeDPIMode = ByeDPIMode.DISORDER
    is_custom: bool = False


@dataclass
class ByeDPIConfig:
    """ByeDPI service configuration."""
    enabled: bool = False
    preset_name: str = "turkey_default"
    custom_args: str = ""
    proxy_host: str = DEFAULT_PROXY_HOST
    proxy_port: int = DEFAULT_PROXY_PORT
    include_browsers: bool = False
    tunneled_apps: list[str] = field(default_factory=list)


# ============================================================================
# Default presets
# ============================================================================

DEFAULT_PRESETS: dict[str, ByeDPIPreset] = {
    "turkey_default": ByeDPIPreset(
        name="Türkiye Varsayılan",
        description="Türkiye için optimize edilmiş varsayılan ayarlar",
        args="--disorder 1 --auto=torst --tlsrec 1+s",
        mode=ByeDPIMode.DISORDER,
    ),
    "turkey_discord": ByeDPIPreset(
        name="Türkiye Discord",
        description="Discord için optimize edilmiş",
        args="--disorder 3 --auto=torst --tlsrec 1+s --fake -1 --ttl 8",
        mode=ByeDPIMode.COMBINED,
    ),
    "preset_disorder": ByeDPIPreset(
        name="Disorder Mode",
        description="Paket sırası karıştırma",
        args="--disorder 1",
        mode=ByeDPIMode.DISORDER,
    ),
    "preset_disorder2": ByeDPIPreset(
        name="Disorder Mode 2",
        description="Gelişmiş paket sırası karıştırma",
        args="--disorder 3",
        mode=ByeDPIMode.DISORDER,
    ),
    "preset_split": ByeDPIPreset(
        name="Split Mode",
        description="Paket bölme",
        args="--split 1",
        mode=ByeDPIMode.SPLIT,
    ),
    "preset_split_tlsrec": ByeDPIPreset(
        name="Split + TLS Record",
        description="Paket bölme ve TLS kayıt bölme",
        args="--split 1 --tlsrec 1+s",
        mode=ByeDPIMode.SPLIT,
    ),
    "preset_fake": ByeDPIPreset(
        name="Fake Mode",
        description="Sahte paket gönderme",
        args="--fake -1 --ttl 8",
        mode=ByeDPIMode.FAKE,
    ),
    "preset_oob": ByeDPIPreset(
        name="OOB Mode",
        description="Out-of-band veri",
        args="--oob 1",
        mode=ByeDPIMode.OOB,
    ),
    "preset_disoob": ByeDPIPreset(
        name="Disorder + OOB",
        description="Disorder ve OOB kombinasyonu",
        args="--disoob 1",
        mode=ByeDPIMode.DISOOB,
    ),
    "preset_auto": ByeDPIPreset(
        name="Auto Mode",
        description="Otomatik tespit ve bypass",
        args="--auto=torst",
        mode=ByeDPIMode.COMBINED,
    ),
}


class ByeDPIService(BaseService):
    """
    ByeDPI proxy service for DPI bypass.

    Runs ciadpi as a SOCKS5 proxy that can bypass DPI restrictions.
    Apps can be routed through the proxy using cgproxy or system proxy settings.
    """

    def __init__(self):
        """Initialize ByeDPI service."""
        super().__init__(
            name="byedpi",
            display_name="ByeDPI Proxy",
            description="SOCKS5 proxy with DPI bypass",
            service_type=ServiceType.PROXY,
        )
        self._config = ByeDPIConfig()
        self._process: Optional[subprocess.Popen] = None
        self._custom_presets: dict[str, ByeDPIPreset] = {}
        self._ensure_directories()
        self._load_config()
        self._load_custom_presets()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                self._config = ByeDPIConfig(
                    enabled=data.get("enabled", False),
                    preset_name=data.get("preset_name", "turkey_default"),
                    custom_args=data.get("custom_args", ""),
                    proxy_host=data.get("proxy_host", DEFAULT_PROXY_HOST),
                    proxy_port=data.get("proxy_port", DEFAULT_PROXY_PORT),
                    include_browsers=data.get("include_browsers", False),
                    tunneled_apps=data.get("tunneled_apps", []),
                )
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        data = {
            "enabled": self._config.enabled,
            "preset_name": self._config.preset_name,
            "custom_args": self._config.custom_args,
            "proxy_host": self._config.proxy_host,
            "proxy_port": self._config.proxy_port,
            "include_browsers": self._config.include_browsers,
            "tunneled_apps": self._config.tunneled_apps,
        }
        CONFIG_FILE.write_text(json.dumps(data, indent=2))

    def _load_custom_presets(self) -> None:
        """Load custom presets from file."""
        if PRESETS_FILE.exists():
            try:
                data = json.loads(PRESETS_FILE.read_text())
                for name, preset_data in data.items():
                    self._custom_presets[name] = ByeDPIPreset(
                        name=preset_data.get("name", name),
                        description=preset_data.get("description", ""),
                        args=preset_data.get("args", ""),
                        mode=ByeDPIMode(preset_data.get("mode", "disorder")),
                        is_custom=True,
                    )
            except Exception as e:
                self._logger.warning(f"Failed to load custom presets: {e}")

    def _save_custom_presets(self) -> None:
        """Save custom presets to file."""
        data = {}
        for name, preset in self._custom_presets.items():
            data[name] = {
                "name": preset.name,
                "description": preset.description,
                "args": preset.args,
                "mode": preset.mode.value,
            }
        PRESETS_FILE.write_text(json.dumps(data, indent=2))

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, preset: Optional[str] = None,
                include_browsers: bool = False,
                one_shot: bool = False,
                as_service: bool = True,
                **kwargs) -> bool:
        """
        Install and start ByeDPI.

        Args:
            preset: Preset name to use (default: turkey_default)
            include_browsers: Route browsers through proxy
            one_shot: Run without installing service (stops when app closes)
            as_service: Install as systemd service

        Returns:
            True if installation successful
        """
        self._logger.info("Installing ByeDPI")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Download ciadpi if not present
            if not self._is_binary_installed():
                self._logger.info("Downloading ciadpi binary...")
                if not self._download_binary():
                    self._logger.error("Failed to download ciadpi")
                    return False

            # Set preset
            preset_name = preset or "turkey_default"
            if preset_name not in self.get_all_presets():
                self._logger.error(f"Unknown preset: {preset_name}")
                return False

            self._config.preset_name = preset_name
            self._config.include_browsers = include_browsers

            # Start the proxy
            if one_shot:
                # Run directly without service
                if not self._start_process():
                    return False
            else:
                # Install and start as service
                if as_service:
                    if not self._install_systemd_service():
                        return False
                    if not self.start():
                        return False
                else:
                    if not self._start_process():
                        return False

            self._config.enabled = True
            self._save_config()

            self._logger.info(f"ByeDPI installed with preset: {preset_name}")
            self._logger.info(f"SOCKS5 proxy: {self._config.proxy_host}:{self._config.proxy_port}")
            return True

        except Exception as e:
            self._logger.exception(f"Installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """Remove ByeDPI service."""
        self._logger.info("Removing ByeDPI")

        try:
            # Stop the service/process
            self.stop()

            # Remove systemd service
            self._remove_systemd_service()

            # Update config
            self._config.enabled = False
            self._save_config()

            self._logger.info("ByeDPI removed")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.exception(f"Removal failed: {e}")
            return False

    def start(self) -> bool:
        """Start ByeDPI service."""
        self._logger.info("Starting ByeDPI")

        # Check if systemd service is installed
        if self._is_service_installed():
            result = self._run_privileged(
                ["systemctl", "start", SYSTEMD_SERVICE],
                timeout=30
            )
            if result.success:
                self._logger.info("ByeDPI started via systemd")
                self._notify_status_change(ServiceStatus.RUNNING)
                return True
            else:
                self._logger.error(f"Failed to start service: {result.stderr}")
                # Fall back to direct start

        # Start directly
        return self._start_process()

    def stop(self) -> bool:
        """Stop ByeDPI."""
        self._logger.info("Stopping ByeDPI")

        # Try systemd first
        if self._is_service_installed():
            result = self._run_privileged(
                ["systemctl", "stop", SYSTEMD_SERVICE],
                timeout=30
            )
            if result.success:
                self._logger.info("ByeDPI stopped via systemd")
                self._notify_status_change(ServiceStatus.STOPPED)
                return True

        # Stop direct process
        return self._stop_process()

    def status(self) -> ServiceStatus:
        """Get ByeDPI status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        # Check systemd service
        if self._is_service_installed():
            result = self._shell.run(
                ["systemctl", "is-active", SYSTEMD_SERVICE],
                timeout=10
            )
            stdout = result.stdout.strip().lower()
            if stdout == "active":
                return ServiceStatus.RUNNING
            elif stdout == "failed":
                return ServiceStatus.FAILED

        # Check for running process
        if self._is_process_running():
            return ServiceStatus.RUNNING

        return ServiceStatus.STOPPED

    def is_installed(self) -> bool:
        """Check if ByeDPI is installed."""
        return self._is_binary_installed() and self._config.enabled

    # =========================================================================
    # ByeDPI specific methods
    # =========================================================================

    def get_config(self) -> ByeDPIConfig:
        """Get current configuration."""
        return self._config

    def get_all_presets(self) -> dict[str, ByeDPIPreset]:
        """Get all available presets (default + custom)."""
        presets = DEFAULT_PRESETS.copy()
        presets.update(self._custom_presets)
        return presets

    def get_preset(self, name: str) -> Optional[ByeDPIPreset]:
        """Get a specific preset by name."""
        return self.get_all_presets().get(name)

    def get_current_preset(self) -> Optional[ByeDPIPreset]:
        """Get the currently selected preset."""
        return self.get_preset(self._config.preset_name)

    def add_custom_preset(self, key: str, preset: ByeDPIPreset) -> bool:
        """
        Add a custom preset.

        Args:
            key: Unique identifier for the preset
            preset: Preset configuration

        Returns:
            True if added successfully
        """
        if key in DEFAULT_PRESETS:
            self._logger.error(f"Cannot override default preset: {key}")
            return False

        preset.is_custom = True
        self._custom_presets[key] = preset
        self._save_custom_presets()
        self._logger.info(f"Added custom preset: {key}")
        return True

    def remove_custom_preset(self, key: str) -> bool:
        """Remove a custom preset."""
        if key in self._custom_presets:
            del self._custom_presets[key]
            self._save_custom_presets()
            self._logger.info(f"Removed custom preset: {key}")
            return True
        return False

    def set_preset(self, name: str) -> bool:
        """
        Set the active preset.

        Args:
            name: Preset name

        Returns:
            True if set successfully
        """
        if name not in self.get_all_presets():
            self._logger.error(f"Unknown preset: {name}")
            return False

        self._config.preset_name = name
        self._save_config()
        return True

    def set_custom_args(self, args: str) -> None:
        """Set custom command line arguments."""
        self._config.custom_args = args
        self._save_config()

    def set_proxy_port(self, port: int) -> None:
        """Set the SOCKS5 proxy port."""
        self._config.proxy_port = port
        self._save_config()

    def get_proxy_address(self) -> str:
        """Get the SOCKS5 proxy address."""
        return f"socks5://{self._config.proxy_host}:{self._config.proxy_port}"

    def set_include_browsers(self, include: bool) -> None:
        """Set whether to include browsers in tunneling."""
        self._config.include_browsers = include
        self._save_config()

    def add_tunneled_app(self, app: str) -> None:
        """Add an app to tunnel through the proxy."""
        if app not in self._config.tunneled_apps:
            self._config.tunneled_apps.append(app)
            self._save_config()

    def remove_tunneled_app(self, app: str) -> None:
        """Remove an app from tunnel list."""
        if app in self._config.tunneled_apps:
            self._config.tunneled_apps.remove(app)
            self._save_config()

    def get_tunneled_apps(self) -> list[str]:
        """Get list of apps tunneled through proxy."""
        return self._config.tunneled_apps.copy()

    def configure(self, preset: Optional[str] = None,
                  custom_params: Optional[str] = None,
                  include_browsers: bool = False) -> bool:
        """
        Configure ByeDPI with specified preset or custom parameters.

        Args:
            preset: Preset name to use
            custom_params: Custom command line arguments
            include_browsers: Include browsers in tunneling

        Returns:
            True if configuration successful
        """
        if preset:
            self._config.preset_name = preset

        if custom_params:
            self._config.custom_args = custom_params

        self._config.include_browsers = include_browsers
        self._save_config()

        self._logger.info(f"ByeDPI configured with preset={preset}, include_browsers={include_browsers}")
        return True

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _is_binary_installed(self) -> bool:
        """Check if ciadpi binary is installed."""
        return BYEDPI_BINARY.exists() and os.access(BYEDPI_BINARY, os.X_OK)

    def _download_binary(self) -> bool:
        """Download ciadpi binary from GitHub releases."""
        try:
            # Get latest release info
            self._logger.info("Fetching latest release info...")
            req = urllib.request.Request(
                CIADPI_RELEASE_URL,
                headers={"User-Agent": "SplitWire-Turkey"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                release_data = json.loads(response.read().decode())

            # Find Linux x86_64 asset
            arch = platform.machine()
            if arch == "x86_64":
                asset_name = "ciadpi-x86_64-linux"
            elif arch == "aarch64":
                asset_name = "ciadpi-aarch64-linux"
            else:
                self._logger.error(f"Unsupported architecture: {arch}")
                return False

            download_url = None
            for asset in release_data.get("assets", []):
                if asset_name in asset.get("name", ""):
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                self._logger.error(f"Could not find asset for {asset_name}")
                return False

            # Create installation directory
            result = self._run_privileged(["mkdir", "-p", str(BYEDPI_INSTALL_DIR)])
            if not result.success:
                return False

            # Download binary
            self._logger.info(f"Downloading from {download_url}")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name

            try:
                req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": "SplitWire-Turkey"}
                )
                with urllib.request.urlopen(req, timeout=120) as response:
                    with open(tmp_path, 'wb') as f:
                        f.write(response.read())

                # Move to installation directory
                result = self._run_privileged(["cp", tmp_path, str(BYEDPI_BINARY)])
                if not result.success:
                    return False

                # Make executable
                result = self._run_privileged(["chmod", "+x", str(BYEDPI_BINARY)])
                if not result.success:
                    return False

                self._logger.info("ciadpi downloaded successfully")
                return True

            finally:
                Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            self._logger.exception(f"Failed to download ciadpi: {e}")
            return False

    def _build_command(self) -> list[str]:
        """Build ciadpi command with arguments."""
        cmd = [str(BYEDPI_BINARY)]

        # Add address and port
        cmd.extend(["-i", f"{self._config.proxy_host}"])
        cmd.extend(["-p", str(self._config.proxy_port)])

        # Add preset args or custom args
        if self._config.custom_args:
            args = self._config.custom_args.split()
        else:
            preset = self.get_current_preset()
            if preset:
                args = preset.args.split()
            else:
                args = []

        cmd.extend(args)
        return cmd

    def _start_process(self) -> bool:
        """Start ciadpi process directly."""
        if self._is_process_running():
            self._logger.info("ByeDPI already running")
            return True

        try:
            cmd = self._build_command()
            self._logger.info(f"Starting: {' '.join(cmd)}")

            # Create PID directory
            result = self._run_privileged(["mkdir", "-p", str(PID_DIR)])

            # Start process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )

            # Wait a moment to check if it started
            time.sleep(0.5)
            if self._process.poll() is not None:
                stdout, stderr = self._process.communicate()
                self._logger.error(f"Process exited: {stderr.decode()}")
                return False

            # Save PID
            self._save_pid(self._process.pid)

            self._logger.info(f"ByeDPI started with PID {self._process.pid}")
            self._notify_status_change(ServiceStatus.RUNNING)
            return True

        except Exception as e:
            self._logger.exception(f"Failed to start process: {e}")
            return False

    def _stop_process(self) -> bool:
        """Stop ciadpi process."""
        try:
            pid = self._get_pid()
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    # Wait for process to exit
                    for _ in range(10):
                        try:
                            os.kill(pid, 0)
                            time.sleep(0.1)
                        except ProcessLookupError:
                            break
                    else:
                        # Force kill if still running
                        os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

                self._remove_pid()

            if self._process:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                self._process = None

            self._logger.info("ByeDPI stopped")
            self._notify_status_change(ServiceStatus.STOPPED)
            return True

        except Exception as e:
            self._logger.exception(f"Failed to stop process: {e}")
            return False

    def _is_process_running(self) -> bool:
        """Check if ciadpi process is running."""
        pid = self._get_pid()
        if pid:
            try:
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                self._remove_pid()
        return False

    def _save_pid(self, pid: int) -> None:
        """Save PID to file."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(str(pid))
                tmp_path = f.name
            self._run_privileged(["cp", tmp_path, str(BYEDPI_PID_FILE)])
            Path(tmp_path).unlink(missing_ok=True)
        except Exception as e:
            self._logger.warning(f"Failed to save PID: {e}")

    def _get_pid(self) -> Optional[int]:
        """Get PID from file."""
        if BYEDPI_PID_FILE.exists():
            try:
                return int(BYEDPI_PID_FILE.read_text().strip())
            except Exception:
                pass
        return None

    def _remove_pid(self) -> None:
        """Remove PID file."""
        try:
            self._run_privileged(["rm", "-f", str(BYEDPI_PID_FILE)])
        except Exception:
            pass

    def _is_service_installed(self) -> bool:
        """Check if systemd service is installed."""
        result = self._shell.run(
            ["systemctl", "list-unit-files", SYSTEMD_SERVICE],
            timeout=10
        )
        return SYSTEMD_SERVICE in result.stdout

    def _install_systemd_service(self) -> bool:
        """Install systemd service file."""
        self._logger.info("Installing systemd service")

        # Get preset args
        preset = self.get_current_preset()
        args = self._config.custom_args or (preset.args if preset else "")

        service_content = f"""[Unit]
Description=SplitWire ByeDPI Proxy Service
Documentation=https://github.com/hufrea/byedpi
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart={BYEDPI_BINARY} -i {self._config.proxy_host} -p {self._config.proxy_port} {args}
Restart=on-failure
RestartSec=5

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
"""

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
                f.write(service_content)
                tmp_path = f.name

            service_path = f"/etc/systemd/system/{SYSTEMD_SERVICE}"
            result = self._run_privileged(["cp", tmp_path, service_path])
            Path(tmp_path).unlink(missing_ok=True)

            if not result.success:
                return False

            # Reload systemd
            self._run_privileged(["systemctl", "daemon-reload"])

            # Enable service
            self._run_privileged(["systemctl", "enable", SYSTEMD_SERVICE])

            return True

        except Exception as e:
            self._logger.exception(f"Failed to install service: {e}")
            return False

    def _remove_systemd_service(self) -> bool:
        """Remove systemd service file."""
        try:
            # Stop and disable
            self._run_privileged(["systemctl", "stop", SYSTEMD_SERVICE])
            self._run_privileged(["systemctl", "disable", SYSTEMD_SERVICE])

            # Remove service file
            self._run_privileged(["rm", "-f", f"/etc/systemd/system/{SYSTEMD_SERVICE}"])

            # Reload systemd
            self._run_privileged(["systemctl", "daemon-reload"])

            return True
        except Exception as e:
            self._logger.warning(f"Failed to remove service: {e}")
            return False


# ============================================================================
# Convenience functions
# ============================================================================

_byedpi_service: Optional[ByeDPIService] = None


def get_byedpi_service() -> ByeDPIService:
    """Get the global ByeDPI service instance."""
    global _byedpi_service
    if _byedpi_service is None:
        _byedpi_service = ByeDPIService()
    return _byedpi_service


if __name__ == "__main__":
    # Test the ByeDPI service
    print("=" * 50)
    print("ByeDPI Service Test")
    print("=" * 50)

    service = ByeDPIService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print(f"\nBinary installed: {service._is_binary_installed()}")
    print(f"Is installed: {service.is_installed()}")
    print(f"Status: {service.status().value}")

    print("\nDefault presets:")
    for name, preset in DEFAULT_PRESETS.items():
        print(f"  {name}: {preset.name}")
        print(f"    Args: {preset.args}")

    config = service.get_config()
    print(f"\nCurrent config:")
    print(f"  Preset: {config.preset_name}")
    print(f"  Proxy: {config.proxy_host}:{config.proxy_port}")
    print(f"  Include browsers: {config.include_browsers}")

    print("\nTest completed!")
