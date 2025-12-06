"""
Zapret DPI bypass service for SplitWire-Turkey Linux.

Provides nfqws and tpws management for bypassing DPI (Deep Packet Inspection).
Equivalent to GoodbyeDPI/Zapret on Windows.
"""

import json
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from splitwire.core import get_logger, get_shell
from splitwire.services.base import BaseService, ServiceStatus, ServiceType


# ============================================================================
# Constants
# ============================================================================

# Zapret installation paths
ZAPRET_INSTALL_DIR = Path("/opt/zapret")
ZAPRET_BIN_DIR = ZAPRET_INSTALL_DIR / "nfq"
ZAPRET_DOCS_DIR = ZAPRET_INSTALL_DIR / "docs"
ZAPRET_FILES_DIR = ZAPRET_INSTALL_DIR / "files"

# Binary paths
NFQWS_BINARY = ZAPRET_BIN_DIR / "nfqws"
TPWS_BINARY = ZAPRET_INSTALL_DIR / "tpws" / "tpws"

# Config directories
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire" / "zapret"
PRESETS_FILE = LOCAL_CONFIG_DIR / "presets.json"
BLACKLIST_FILE = LOCAL_CONFIG_DIR / "blacklist.txt"
CUSTOM_CONFIG_FILE = LOCAL_CONFIG_DIR / "custom.json"

# PID files for process tracking
PID_DIR = Path("/run/splitwire")
NFQWS_PID_FILE = PID_DIR / "nfqws.pid"
TPWS_PID_FILE = PID_DIR / "tpws.pid"

# GitHub repository
ZAPRET_REPO = "https://github.com/bol-van/zapret.git"
ZAPRET_REPO_BRANCH = "master"

# Default ports to filter
DEFAULT_HTTP_PORTS = [80]
DEFAULT_HTTPS_PORTS = [443]
DEFAULT_QUIC_PORTS = [443]

# iptables marks
NFQUEUE_NUM = 200
TPWS_PORT = 988

# Default excluded networks (don't route through zapret)
DEFAULT_EXCLUDED_NETWORKS = [
    "127.0.0.0/8",      # Loopback
    "10.0.0.0/8",       # Private
    "172.16.0.0/12",    # Private
    "192.168.0.0/16",   # Private
]


class ZapretMode(Enum):
    """Zapret operation mode."""
    NFQWS = "nfqws"      # Netfilter queue (packet modification)
    TPWS = "tpws"        # Transparent proxy
    COMBINED = "combined"  # Both modes


class ScanMode(Enum):
    """Blockcheck scan mode."""
    QUICK = "quick"       # Hızlı - basic scan
    STANDARD = "standard" # Standart - moderate scan
    FULL = "full"         # Tam - comprehensive scan


@dataclass
class ZapretPreset:
    """Configuration preset for Zapret."""
    name: str
    description: str
    nfqws_args: str = ""
    tpws_args: str = ""
    mode: ZapretMode = ZapretMode.NFQWS
    use_blacklist: bool = False
    is_custom: bool = False


@dataclass
class ZapretConfig:
    """Zapret service configuration."""
    enabled: bool = False
    mode: ZapretMode = ZapretMode.NFQWS
    preset_name: str = "turkey_discord"
    custom_nfqws_args: str = ""
    custom_tpws_args: str = ""
    use_blacklist: bool = False
    http_ports: list[int] = field(default_factory=lambda: [80])
    https_ports: list[int] = field(default_factory=lambda: [443])
    quic_enabled: bool = False


# ============================================================================
# Default presets (equivalent to Windows presets)
# ============================================================================

DEFAULT_PRESETS: dict[str, ZapretPreset] = {
    "turkey_discord": ZapretPreset(
        name="Türkiye Discord",
        description="Discord için optimize edilmiş ayarlar",
        nfqws_args="--dpi-desync=fake,split2 --dpi-desync-ttl=5 --dpi-desync-fooling=md5sig",
        mode=ZapretMode.NFQWS,
    ),
    "turkey_general": ZapretPreset(
        name="Türkiye Genel",
        description="Genel kullanım için ayarlar",
        nfqws_args="--dpi-desync=fake,disorder2 --dpi-desync-ttl=8 --dpi-desync-fooling=md5sig",
        mode=ZapretMode.NFQWS,
    ),
    "turkey_youtube": ZapretPreset(
        name="Türkiye YouTube",
        description="YouTube için optimize edilmiş",
        nfqws_args="--dpi-desync=fake,split2 --dpi-desync-ttl=4 --dpi-desync-fooling=md5sig,badseq",
        mode=ZapretMode.NFQWS,
    ),
    "preset_split": ZapretPreset(
        name="Split Mode",
        description="Paket bölme yöntemi",
        nfqws_args="--dpi-desync=split2 --dpi-desync-split-pos=3",
        mode=ZapretMode.NFQWS,
    ),
    "preset_fake": ZapretPreset(
        name="Fake Mode",
        description="Sahte paket yöntemi",
        nfqws_args="--dpi-desync=fake --dpi-desync-ttl=6",
        mode=ZapretMode.NFQWS,
    ),
    "preset_disorder": ZapretPreset(
        name="Disorder Mode",
        description="Paket sırası karıştırma",
        nfqws_args="--dpi-desync=disorder2 --dpi-desync-ttl=8",
        mode=ZapretMode.NFQWS,
    ),
    "preset_tpws": ZapretPreset(
        name="TPWS Mode",
        description="Transparent proxy yöntemi",
        tpws_args="--split-pos=3 --disorder",
        mode=ZapretMode.TPWS,
    ),
    "preset_combined": ZapretPreset(
        name="Combined Mode",
        description="nfqws + tpws birlikte",
        nfqws_args="--dpi-desync=fake,split2 --dpi-desync-ttl=5",
        tpws_args="--split-pos=3",
        mode=ZapretMode.COMBINED,
    ),
}


# ============================================================================
# Zapret Service
# ============================================================================

class ZapretService(BaseService):
    """
    Zapret DPI bypass service manager.

    Manages:
    - nfqws: Netfilter queue-based packet manipulation
    - tpws: Transparent proxy for DPI bypass
    - iptables rules for traffic redirection
    - Presets and custom configurations
    """

    def __init__(self):
        super().__init__(
            name="zapret",
            display_name="Zapret DPI Bypass",
            description="DPI bypass using nfqws/tpws packet manipulation",
            service_type=ServiceType.DPI_BYPASS,
        )
        self._config = ZapretConfig()
        self._presets: dict[str, ZapretPreset] = {}
        self._nfqws_process: Optional[subprocess.Popen] = None
        self._tpws_process: Optional[subprocess.Popen] = None

        # Load presets
        self._load_presets()
        self._load_config()

        # Ensure config directory exists
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Installation
    # =========================================================================

    def install(self, **kwargs) -> bool:
        """
        Install Zapret from source.

        Steps:
        1. Install dependencies
        2. Clone zapret repository
        3. Build binaries
        4. Create config directories
        5. Install systemd service

        Returns:
            True if installation successful
        """
        self._logger.info("Installing Zapret...")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Step 1: Check and install dependencies
            if not self._install_dependencies():
                self._logger.error("Failed to install dependencies")
                return False

            # Step 2: Clone or update repository
            if not self._clone_zapret():
                self._logger.error("Failed to clone Zapret repository")
                return False

            # Step 3: Build binaries
            if not self._build_zapret():
                self._logger.error("Failed to build Zapret binaries")
                return False

            # Step 4: Create config directories
            self._setup_config_dirs()

            # Step 5: Install systemd service
            self._install_systemd_service()

            # Step 6: Save default presets
            self._save_presets()

            self._logger.info("Zapret installed successfully")
            self._notify_status_change(ServiceStatus.STOPPED)
            return True

        except Exception as e:
            self._logger.error(f"Installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """
        Remove Zapret installation.

        Returns:
            True if removal successful
        """
        self._logger.info("Removing Zapret...")
        self._notify_status_change(ServiceStatus.REMOVING)

        try:
            # Stop service first
            if self.is_running():
                self.stop()

            # Remove systemd service
            self._remove_systemd_service()

            # Remove installation directory
            if ZAPRET_INSTALL_DIR.exists():
                result = self._run_privileged(
                    ["rm", "-rf", str(ZAPRET_INSTALL_DIR)],
                    timeout=60
                )
                if not result.success:
                    self._logger.warning(f"Failed to remove {ZAPRET_INSTALL_DIR}")

            self._logger.info("Zapret removed successfully")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.error(f"Removal failed: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if Zapret is installed."""
        return NFQWS_BINARY.exists() or TPWS_BINARY.exists()

    # =========================================================================
    # Service Control
    # =========================================================================

    def start(self, one_shot: bool = False) -> bool:
        """
        Start Zapret service.

        Args:
            one_shot: If True, run without installing service (Tek Seferlik)

        Returns:
            True if started successfully
        """
        if not self.is_installed():
            self._logger.error("Zapret is not installed")
            return False

        if self.is_running():
            self._logger.warning("Zapret is already running")
            return True

        self._logger.info(f"Starting Zapret in {self._config.mode.value} mode")

        try:
            # Get current preset
            preset = self._get_current_preset()

            # Add iptables rules first
            if not self._add_iptables_rules():
                self._logger.error("Failed to add iptables rules")
                return False

            # Start appropriate process(es)
            mode = preset.mode if preset else self._config.mode

            if mode in [ZapretMode.NFQWS, ZapretMode.COMBINED]:
                if not self._start_nfqws(preset, one_shot):
                    self._remove_iptables_rules()
                    return False

            if mode in [ZapretMode.TPWS, ZapretMode.COMBINED]:
                if not self._start_tpws(preset, one_shot):
                    self._stop_nfqws()
                    self._remove_iptables_rules()
                    return False

            self._config.enabled = True
            self._save_config()
            self._notify_status_change(ServiceStatus.RUNNING)
            self._logger.info("Zapret started successfully")
            return True

        except Exception as e:
            self._logger.error(f"Failed to start Zapret: {e}")
            self.stop()
            return False

    def stop(self) -> bool:
        """Stop Zapret service."""
        self._logger.info("Stopping Zapret...")

        try:
            # Stop processes
            self._stop_nfqws()
            self._stop_tpws()

            # Remove iptables rules
            self._remove_iptables_rules()

            self._config.enabled = False
            self._save_config()
            self._notify_status_change(ServiceStatus.STOPPED)
            self._logger.info("Zapret stopped")
            return True

        except Exception as e:
            self._logger.error(f"Failed to stop Zapret: {e}")
            return False

    def status(self) -> ServiceStatus:
        """Get Zapret service status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        if self._is_nfqws_running() or self._is_tpws_running():
            return ServiceStatus.RUNNING

        return ServiceStatus.STOPPED

    # =========================================================================
    # nfqws Management
    # =========================================================================

    def _start_nfqws(self, preset: Optional[ZapretPreset], one_shot: bool = False) -> bool:
        """Start nfqws process."""
        if not NFQWS_BINARY.exists():
            self._logger.error(f"nfqws binary not found at {NFQWS_BINARY}")
            return False

        # Build command arguments
        args = self._build_nfqws_args(preset)
        cmd = [str(NFQWS_BINARY)] + args

        self._logger.debug(f"Starting nfqws: {' '.join(cmd)}")

        try:
            # Create PID directory if needed
            PID_DIR.mkdir(parents=True, exist_ok=True)

            # Start process
            self._nfqws_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            # Save PID
            NFQWS_PID_FILE.write_text(str(self._nfqws_process.pid))

            # Wait briefly to check if process started
            time.sleep(0.5)
            if self._nfqws_process.poll() is not None:
                self._logger.error("nfqws process terminated immediately")
                return False

            self._logger.info(f"nfqws started with PID {self._nfqws_process.pid}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to start nfqws: {e}")
            return False

    def _stop_nfqws(self) -> bool:
        """Stop nfqws process."""
        try:
            # Try to get PID from file
            pid = None
            if NFQWS_PID_FILE.exists():
                try:
                    pid = int(NFQWS_PID_FILE.read_text().strip())
                except (ValueError, OSError):
                    pass

            # Also check our tracked process
            if self._nfqws_process and self._nfqws_process.poll() is None:
                pid = self._nfqws_process.pid

            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.5)
                    # Force kill if still running
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                except ProcessLookupError:
                    pass  # Already dead

            # Also kill any remaining nfqws processes
            self._shell.run(["pkill", "-9", "nfqws"], timeout=5)

            # Cleanup PID file
            if NFQWS_PID_FILE.exists():
                NFQWS_PID_FILE.unlink()

            self._nfqws_process = None
            return True

        except Exception as e:
            self._logger.error(f"Error stopping nfqws: {e}")
            return False

    def _is_nfqws_running(self) -> bool:
        """Check if nfqws is running."""
        result = self._shell.run(["pgrep", "-x", "nfqws"], timeout=5)
        return result.success

    def _build_nfqws_args(self, preset: Optional[ZapretPreset]) -> list[str]:
        """Build nfqws command line arguments."""
        args = []

        # Queue number
        args.extend(["--qnum", str(NFQUEUE_NUM)])

        # Get args from preset or custom config
        if preset and preset.nfqws_args:
            args.extend(preset.nfqws_args.split())
        elif self._config.custom_nfqws_args:
            args.extend(self._config.custom_nfqws_args.split())
        else:
            # Default args
            args.extend([
                "--dpi-desync=fake,split2",
                "--dpi-desync-ttl=5",
                "--dpi-desync-fooling=md5sig",
            ])

        # Blacklist support
        if (preset and preset.use_blacklist) or self._config.use_blacklist:
            if BLACKLIST_FILE.exists():
                args.extend(["--hostlist", str(BLACKLIST_FILE)])

        return args

    # =========================================================================
    # tpws Management
    # =========================================================================

    def _start_tpws(self, preset: Optional[ZapretPreset], one_shot: bool = False) -> bool:
        """Start tpws process."""
        if not TPWS_BINARY.exists():
            self._logger.error(f"tpws binary not found at {TPWS_BINARY}")
            return False

        # Build command arguments
        args = self._build_tpws_args(preset)
        cmd = [str(TPWS_BINARY)] + args

        self._logger.debug(f"Starting tpws: {' '.join(cmd)}")

        try:
            # Create PID directory if needed
            PID_DIR.mkdir(parents=True, exist_ok=True)

            # Start process
            self._tpws_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            # Save PID
            TPWS_PID_FILE.write_text(str(self._tpws_process.pid))

            # Wait briefly to check if process started
            time.sleep(0.5)
            if self._tpws_process.poll() is not None:
                self._logger.error("tpws process terminated immediately")
                return False

            self._logger.info(f"tpws started with PID {self._tpws_process.pid}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to start tpws: {e}")
            return False

    def _stop_tpws(self) -> bool:
        """Stop tpws process."""
        try:
            # Try to get PID from file
            pid = None
            if TPWS_PID_FILE.exists():
                try:
                    pid = int(TPWS_PID_FILE.read_text().strip())
                except (ValueError, OSError):
                    pass

            # Also check our tracked process
            if self._tpws_process and self._tpws_process.poll() is None:
                pid = self._tpws_process.pid

            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.5)
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                except ProcessLookupError:
                    pass

            # Also kill any remaining tpws processes
            self._shell.run(["pkill", "-9", "tpws"], timeout=5)

            # Cleanup PID file
            if TPWS_PID_FILE.exists():
                TPWS_PID_FILE.unlink()

            self._tpws_process = None
            return True

        except Exception as e:
            self._logger.error(f"Error stopping tpws: {e}")
            return False

    def _is_tpws_running(self) -> bool:
        """Check if tpws is running."""
        result = self._shell.run(["pgrep", "-x", "tpws"], timeout=5)
        return result.success

    def _build_tpws_args(self, preset: Optional[ZapretPreset]) -> list[str]:
        """Build tpws command line arguments."""
        args = []

        # Bind to transparent proxy port
        args.extend(["--port", str(TPWS_PORT)])
        args.append("--bind-addr=127.0.0.1")

        # Get args from preset or custom config
        if preset and preset.tpws_args:
            args.extend(preset.tpws_args.split())
        elif self._config.custom_tpws_args:
            args.extend(self._config.custom_tpws_args.split())
        else:
            # Default args
            args.extend([
                "--split-pos=3",
                "--disorder",
            ])

        # Blacklist support
        if (preset and preset.use_blacklist) or self._config.use_blacklist:
            if BLACKLIST_FILE.exists():
                args.extend(["--hostlist", str(BLACKLIST_FILE)])

        return args

    # =========================================================================
    # iptables Rules
    # =========================================================================

    def _add_iptables_rules(self) -> bool:
        """Add iptables rules for traffic redirection."""
        try:
            mode = self._get_current_mode()
            http_ports = self._config.http_ports or DEFAULT_HTTP_PORTS
            https_ports = self._config.https_ports or DEFAULT_HTTPS_PORTS

            # Build port string
            http_ports_str = ",".join(str(p) for p in http_ports)
            https_ports_str = ",".join(str(p) for p in https_ports)

            rules_added = []

            if mode in [ZapretMode.NFQWS, ZapretMode.COMBINED]:
                # NFQUEUE rules for nfqws
                # HTTP
                for port in http_ports:
                    result = self._run_privileged([
                        "iptables", "-t", "mangle", "-A", "POSTROUTING",
                        "-p", "tcp", "--dport", str(port),
                        "-j", "NFQUEUE", "--queue-num", str(NFQUEUE_NUM)
                    ])
                    if result.success:
                        rules_added.append(f"NFQUEUE HTTP {port}")

                # HTTPS
                for port in https_ports:
                    result = self._run_privileged([
                        "iptables", "-t", "mangle", "-A", "POSTROUTING",
                        "-p", "tcp", "--dport", str(port),
                        "-j", "NFQUEUE", "--queue-num", str(NFQUEUE_NUM)
                    ])
                    if result.success:
                        rules_added.append(f"NFQUEUE HTTPS {port}")

            if mode in [ZapretMode.TPWS, ZapretMode.COMBINED]:
                # REDIRECT rules for tpws
                for port in https_ports:
                    result = self._run_privileged([
                        "iptables", "-t", "nat", "-A", "OUTPUT",
                        "-p", "tcp", "--dport", str(port),
                        "-j", "REDIRECT", "--to-port", str(TPWS_PORT)
                    ])
                    if result.success:
                        rules_added.append(f"REDIRECT {port}")

            self._logger.debug(f"Added iptables rules: {rules_added}")
            return len(rules_added) > 0

        except Exception as e:
            self._logger.error(f"Failed to add iptables rules: {e}")
            return False

    def _remove_iptables_rules(self) -> bool:
        """Remove all iptables rules added by zapret."""
        try:
            http_ports = self._config.http_ports or DEFAULT_HTTP_PORTS
            https_ports = self._config.https_ports or DEFAULT_HTTPS_PORTS

            # Remove NFQUEUE rules
            for port in http_ports + https_ports:
                self._run_privileged([
                    "iptables", "-t", "mangle", "-D", "POSTROUTING",
                    "-p", "tcp", "--dport", str(port),
                    "-j", "NFQUEUE", "--queue-num", str(NFQUEUE_NUM)
                ])

            # Remove REDIRECT rules
            for port in https_ports:
                self._run_privileged([
                    "iptables", "-t", "nat", "-D", "OUTPUT",
                    "-p", "tcp", "--dport", str(port),
                    "-j", "REDIRECT", "--to-port", str(TPWS_PORT)
                ])

            self._logger.debug("Removed iptables rules")
            return True

        except Exception as e:
            self._logger.error(f"Failed to remove iptables rules: {e}")
            return False

    # =========================================================================
    # Preset Management
    # =========================================================================

    def get_presets(self) -> dict[str, ZapretPreset]:
        """Get all available presets."""
        return self._presets.copy()

    def get_preset(self, name: str) -> Optional[ZapretPreset]:
        """Get a specific preset by name."""
        return self._presets.get(name)

    def set_preset(self, name: str) -> bool:
        """Set active preset."""
        if name not in self._presets:
            self._logger.error(f"Preset '{name}' not found")
            return False

        self._config.preset_name = name
        self._save_config()

        # Restart if running
        if self.is_running():
            return self.restart()
        return True

    def add_custom_preset(self, name: str, preset: ZapretPreset) -> bool:
        """Add a custom preset."""
        preset.is_custom = True
        self._presets[name] = preset
        self._save_presets()
        return True

    def remove_custom_preset(self, name: str) -> bool:
        """Remove a custom preset."""
        if name not in self._presets:
            return False
        if not self._presets[name].is_custom:
            self._logger.error("Cannot remove built-in preset")
            return False
        del self._presets[name]
        self._save_presets()
        return True

    def _get_current_preset(self) -> Optional[ZapretPreset]:
        """Get currently active preset."""
        return self._presets.get(self._config.preset_name)

    def _get_current_mode(self) -> ZapretMode:
        """Get current operation mode."""
        preset = self._get_current_preset()
        return preset.mode if preset else self._config.mode

    def _load_presets(self) -> None:
        """Load presets from file or use defaults."""
        self._presets = DEFAULT_PRESETS.copy()

        if PRESETS_FILE.exists():
            try:
                data = json.loads(PRESETS_FILE.read_text())
                for name, preset_data in data.get("custom_presets", {}).items():
                    self._presets[name] = ZapretPreset(
                        name=preset_data.get("name", name),
                        description=preset_data.get("description", ""),
                        nfqws_args=preset_data.get("nfqws_args", ""),
                        tpws_args=preset_data.get("tpws_args", ""),
                        mode=ZapretMode(preset_data.get("mode", "nfqws")),
                        use_blacklist=preset_data.get("use_blacklist", False),
                        is_custom=True,
                    )
            except Exception as e:
                self._logger.warning(f"Failed to load presets: {e}")

    def _save_presets(self) -> None:
        """Save custom presets to file."""
        try:
            LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            custom_presets = {}
            for name, preset in self._presets.items():
                if preset.is_custom:
                    custom_presets[name] = {
                        "name": preset.name,
                        "description": preset.description,
                        "nfqws_args": preset.nfqws_args,
                        "tpws_args": preset.tpws_args,
                        "mode": preset.mode.value,
                        "use_blacklist": preset.use_blacklist,
                    }

            data = {"custom_presets": custom_presets}
            PRESETS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            self._logger.error(f"Failed to save presets: {e}")

    # =========================================================================
    # Blacklist Management
    # =========================================================================

    def get_blacklist(self) -> list[str]:
        """Get current blacklist domains."""
        if not BLACKLIST_FILE.exists():
            return []
        try:
            content = BLACKLIST_FILE.read_text()
            return [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
        except Exception:
            return []

    def set_blacklist(self, domains: list[str]) -> bool:
        """Set blacklist domains."""
        try:
            LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            content = "# SplitWire Zapret Blacklist\n"
            content += "# One domain per line\n\n"
            content += "\n".join(domains)
            BLACKLIST_FILE.write_text(content)
            return True
        except Exception as e:
            self._logger.error(f"Failed to save blacklist: {e}")
            return False

    def add_to_blacklist(self, domain: str) -> bool:
        """Add domain to blacklist."""
        domains = self.get_blacklist()
        if domain not in domains:
            domains.append(domain)
            return self.set_blacklist(domains)
        return True

    def remove_from_blacklist(self, domain: str) -> bool:
        """Remove domain from blacklist."""
        domains = self.get_blacklist()
        if domain in domains:
            domains.remove(domain)
            return self.set_blacklist(domains)
        return True

    def set_use_blacklist(self, enabled: bool) -> bool:
        """Enable or disable blacklist filtering."""
        self._config.use_blacklist = enabled
        self._save_config()
        if self.is_running():
            return self.restart()
        return True

    # =========================================================================
    # Custom Parameters
    # =========================================================================

    def set_custom_nfqws_args(self, args: str) -> bool:
        """Set custom nfqws arguments."""
        self._config.custom_nfqws_args = args
        self._save_config()
        return True

    def set_custom_tpws_args(self, args: str) -> bool:
        """Set custom tpws arguments."""
        self._config.custom_tpws_args = args
        self._save_config()
        return True

    def set_mode(self, mode: ZapretMode) -> bool:
        """Set operation mode."""
        self._config.mode = mode
        self._save_config()
        if self.is_running():
            return self.restart()
        return True

    # =========================================================================
    # Configuration
    # =========================================================================

    def _load_config(self) -> None:
        """Load configuration from file."""
        if CUSTOM_CONFIG_FILE.exists():
            try:
                data = json.loads(CUSTOM_CONFIG_FILE.read_text())
                self._config = ZapretConfig(
                    enabled=data.get("enabled", False),
                    mode=ZapretMode(data.get("mode", "nfqws")),
                    preset_name=data.get("preset_name", "turkey_discord"),
                    custom_nfqws_args=data.get("custom_nfqws_args", ""),
                    custom_tpws_args=data.get("custom_tpws_args", ""),
                    use_blacklist=data.get("use_blacklist", False),
                    http_ports=data.get("http_ports", [80]),
                    https_ports=data.get("https_ports", [443]),
                    quic_enabled=data.get("quic_enabled", False),
                )
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "enabled": self._config.enabled,
                "mode": self._config.mode.value,
                "preset_name": self._config.preset_name,
                "custom_nfqws_args": self._config.custom_nfqws_args,
                "custom_tpws_args": self._config.custom_tpws_args,
                "use_blacklist": self._config.use_blacklist,
                "http_ports": self._config.http_ports,
                "https_ports": self._config.https_ports,
                "quic_enabled": self._config.quic_enabled,
            }
            CUSTOM_CONFIG_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self._logger.error(f"Failed to save config: {e}")

    def get_config(self) -> ZapretConfig:
        """Get current configuration."""
        return self._config

    # =========================================================================
    # Installation Helpers
    # =========================================================================

    def _install_dependencies(self) -> bool:
        """Install required system dependencies."""
        self._logger.info("Installing Zapret dependencies...")

        # Required packages
        packages = [
            "git",
            "make",
            "gcc",
            "libnetfilter-queue-dev",
            "libcap-dev",
            "libnfnetlink-dev",
            "zlib1g-dev",
            "iptables",
        ]

        # Detect package manager
        if self._shell.command_exists("apt-get"):
            cmd = ["apt-get", "update"]
            self._run_privileged(cmd, timeout=120)
            cmd = ["apt-get", "install", "-y"] + packages
        elif self._shell.command_exists("dnf"):
            # Fedora/RHEL
            packages = [
                "git", "make", "gcc",
                "libnetfilter_queue-devel",
                "libcap-devel", "libnfnetlink-devel",
                "zlib-devel", "iptables",
            ]
            cmd = ["dnf", "install", "-y"] + packages
        elif self._shell.command_exists("pacman"):
            # Arch
            packages = [
                "git", "make", "gcc",
                "libnetfilter_queue",
                "libcap", "libnfnetlink",
                "zlib", "iptables",
            ]
            cmd = ["pacman", "-S", "--noconfirm"] + packages
        else:
            self._logger.error("Unsupported package manager")
            return False

        result = self._run_privileged(cmd, timeout=300)
        if not result.success:
            self._logger.error(f"Failed to install packages: {result.stderr}")
            return False

        return True

    def _clone_zapret(self) -> bool:
        """Clone or update zapret repository."""
        self._logger.info("Cloning Zapret repository...")

        # Create parent directory
        result = self._run_privileged(
            ["mkdir", "-p", str(ZAPRET_INSTALL_DIR.parent)],
            timeout=30
        )

        if ZAPRET_INSTALL_DIR.exists():
            # Update existing repo
            self._logger.info("Updating existing Zapret installation...")
            result = self._run_privileged(
                ["git", "-C", str(ZAPRET_INSTALL_DIR), "pull"],
                timeout=300
            )
        else:
            # Clone new repo
            result = self._run_privileged([
                "git", "clone", "--depth=1",
                "-b", ZAPRET_REPO_BRANCH,
                ZAPRET_REPO,
                str(ZAPRET_INSTALL_DIR)
            ], timeout=300)

        if not result.success:
            self._logger.error(f"Git operation failed: {result.stderr}")
            return False

        return True

    def _build_zapret(self) -> bool:
        """Build zapret binaries."""
        self._logger.info("Building Zapret binaries...")

        # Run make in nfq directory for nfqws
        if (ZAPRET_INSTALL_DIR / "nfq").exists():
            result = self._run_privileged(
                ["make", "-C", str(ZAPRET_INSTALL_DIR / "nfq")],
                timeout=300
            )
            if not result.success:
                self._logger.warning(f"nfqws build warning: {result.stderr}")

        # Run make in tpws directory
        if (ZAPRET_INSTALL_DIR / "tpws").exists():
            result = self._run_privileged(
                ["make", "-C", str(ZAPRET_INSTALL_DIR / "tpws")],
                timeout=300
            )
            if not result.success:
                self._logger.warning(f"tpws build warning: {result.stderr}")

        # Verify at least one binary was built
        if not NFQWS_BINARY.exists() and not TPWS_BINARY.exists():
            self._logger.error("No binaries were built")
            return False

        self._logger.info("Zapret binaries built successfully")
        return True

    def _setup_config_dirs(self) -> None:
        """Create configuration directories."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Create default blacklist
        if not BLACKLIST_FILE.exists():
            default_domains = [
                "discord.com",
                "discord.gg",
                "discordapp.com",
                "discord.media",
                "discordcdn.com",
                "gateway.discord.gg",
            ]
            self.set_blacklist(default_domains)

    def _install_systemd_service(self) -> bool:
        """Install systemd service file."""
        service_content = f"""[Unit]
Description=SplitWire Zapret DPI Bypass
After=network.target

[Service]
Type=forking
ExecStart=/usr/bin/python3 -c "from splitwire.services.zapret import get_zapret_service; get_zapret_service().start()"
ExecStop=/usr/bin/python3 -c "from splitwire.services.zapret import get_zapret_service; get_zapret_service().stop()"
RemainAfterExit=yes
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        service_file = Path("/etc/systemd/system/splitwire-zapret.service")

        # Write using privileged command
        result = self._run_privileged(
            ["tee", str(service_file)],
            input_data=service_content,
            timeout=30
        )

        if result.success:
            # Reload systemd
            self._run_privileged(["systemctl", "daemon-reload"])

        return result.success

    def _remove_systemd_service(self) -> bool:
        """Remove systemd service file."""
        service_file = Path("/etc/systemd/system/splitwire-zapret.service")

        # Disable and stop first
        self._run_privileged(["systemctl", "disable", "splitwire-zapret.service"])
        self._run_privileged(["systemctl", "stop", "splitwire-zapret.service"])

        # Remove file
        if service_file.exists():
            result = self._run_privileged(["rm", "-f", str(service_file)])
            self._run_privileged(["systemctl", "daemon-reload"])
            return result.success

        return True


# ============================================================================
# Module-level singleton
# ============================================================================

_zapret_service: Optional[ZapretService] = None


def get_zapret_service() -> ZapretService:
    """Get the singleton Zapret service instance."""
    global _zapret_service
    if _zapret_service is None:
        _zapret_service = ZapretService()
    return _zapret_service


# ============================================================================
# Main for testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Zapret Service Test")
    print("=" * 60)

    service = get_zapret_service()

    print(f"\nService: {service.display_name}")
    print(f"Status: {service.status().value}")
    print(f"Installed: {service.is_installed()}")

    print("\nAvailable presets:")
    for name, preset in service.get_presets().items():
        print(f"  - {name}: {preset.name}")
        print(f"    Mode: {preset.mode.value}")
        print(f"    Args: {preset.nfqws_args or preset.tpws_args}")

    print("\nBlacklist domains:")
    for domain in service.get_blacklist():
        print(f"  - {domain}")
