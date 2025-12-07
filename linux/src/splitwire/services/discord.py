"""
Discord repair and management service for SplitWire-Turkey Linux.

Provides Discord detection, repair, and alternative client installation.
Supports Discord Stable, PTB, Canary, and WebCord.
"""

import json
import shutil
import subprocess
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime

from splitwire.core import get_logger, get_shell
from splitwire.services.base import BaseService, ServiceStatus, ServiceType


# ============================================================================
# Constants
# ============================================================================

# Configuration paths
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire" / "discord"
CONFIG_FILE = LOCAL_CONFIG_DIR / "config.json"

# Discord paths
DISCORD_CONFIG_DIRS = {
    "stable": Path.home() / ".config" / "discord",
    "ptb": Path.home() / ".config" / "discordptb",
    "canary": Path.home() / ".config" / "discordcanary",
}

DISCORD_CACHE_DIRS = {
    "stable": Path.home() / ".cache" / "discord",
    "ptb": Path.home() / ".cache" / "discordptb",
    "canary": Path.home() / ".cache" / "discordcanary",
}

# Flatpak Discord paths
FLATPAK_DISCORD_IDS = {
    "stable": "com.discordapp.Discord",
    "ptb": "com.discordapp.DiscordPTB",
    "canary": "com.discordapp.DiscordCanary",
}

# Snap Discord names
SNAP_DISCORD_NAMES = {
    "stable": "discord",
    "ptb": "discord-ptb",
    "canary": "discord-canary",
}

# DEB package names
DEB_DISCORD_NAMES = {
    "stable": "discord",
    "ptb": "discord-ptb",
    "canary": "discord-canary",
}

# Binary names
DISCORD_BINARIES = {
    "stable": ["discord", "Discord"],
    "ptb": ["discord-ptb", "discordptb", "DiscordPTB"],
    "canary": ["discord-canary", "discordcanary", "DiscordCanary"],
}

# Download URLs
DISCORD_DOWNLOAD_URLS = {
    "stable": "https://discord.com/api/download?platform=linux&format=deb",
    "ptb": "https://discord.com/api/download/ptb?platform=linux&format=deb",
    "canary": "https://discord.com/api/download/canary?platform=linux&format=deb",
}

# WebCord
WEBCORD_FLATPAK_ID = "io.github.nickvision.webcord"
WEBCORD_APPIMAGE_URL = "https://github.com/nickvision/webcord/releases/latest"


class DiscordVersion(Enum):
    """Discord version/channel."""
    STABLE = "stable"
    PTB = "ptb"
    CANARY = "canary"


class InstallMethod(Enum):
    """Discord installation method."""
    DEB = "deb"
    SNAP = "snap"
    FLATPAK = "flatpak"
    TARBALL = "tarball"
    APPIMAGE = "appimage"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"


@dataclass
class DiscordInstallation:
    """Information about a Discord installation."""
    version: DiscordVersion
    method: InstallMethod
    path: Optional[str] = None
    binary_path: Optional[str] = None
    config_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    is_running: bool = False
    has_cache: bool = False
    cache_size_mb: float = 0.0


@dataclass
class WebCordInstallation:
    """Information about WebCord installation."""
    installed: bool = False
    method: InstallMethod = InstallMethod.NOT_INSTALLED
    path: Optional[str] = None
    is_running: bool = False


@dataclass
class DiscordConfig:
    """Discord service configuration."""
    last_repair_date: Optional[str] = None
    auto_clear_cache: bool = False
    preferred_version: str = "stable"


@dataclass
class RepairResult:
    """Result of a repair operation."""
    success: bool
    message: str
    cache_cleared_mb: float = 0.0
    errors: list[str] = field(default_factory=list)


class DiscordService(BaseService):
    """
    Discord repair and management service.

    Provides:
    - Detection of Discord installations (deb, snap, flatpak, tarball)
    - Detection of Discord versions (Stable, PTB, Canary)
    - Cache clearing and repair
    - Discord PTB/Canary installation
    - WebCord installation
    """

    def __init__(self):
        """Initialize Discord service."""
        super().__init__(
            name="discord",
            display_name="Discord Repair",
            description="Discord detection, repair, and alternative clients",
            service_type=ServiceType.SYSTEM,
        )
        self._config = DiscordConfig()
        self._installations: dict[DiscordVersion, DiscordInstallation] = {}
        self._webcord: Optional[WebCordInstallation] = None
        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                self._config = DiscordConfig(
                    last_repair_date=data.get("last_repair_date"),
                    auto_clear_cache=data.get("auto_clear_cache", False),
                    preferred_version=data.get("preferred_version", "stable"),
                )
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        data = {
            "last_repair_date": self._config.last_repair_date,
            "auto_clear_cache": self._config.auto_clear_cache,
            "preferred_version": self._config.preferred_version,
        }
        CONFIG_FILE.write_text(json.dumps(data, indent=2))

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, version: str = "stable", **kwargs) -> bool:
        """
        Install Discord version.

        Args:
            version: Discord version to install (stable, ptb, canary)

        Returns:
            True if installation successful
        """
        try:
            discord_version = DiscordVersion(version.lower())
        except ValueError:
            self._logger.error(f"Invalid Discord version: {version}")
            return False

        return self.install_discord(discord_version)

    def remove(self) -> bool:
        """Remove is not applicable for Discord service."""
        self._logger.info("Use uninstall_discord() for specific version removal")
        return True

    def start(self) -> bool:
        """Launch Discord."""
        return self.launch_discord()

    def stop(self) -> bool:
        """Stop/kill Discord processes."""
        return self.kill_discord()

    def status(self) -> ServiceStatus:
        """Get Discord status."""
        self.detect_all()

        # Check if any Discord is installed
        has_installed = any(
            inst.method != InstallMethod.NOT_INSTALLED
            for inst in self._installations.values()
        )

        if not has_installed:
            return ServiceStatus.NOT_INSTALLED

        # Check if any is running
        has_running = any(
            inst.is_running
            for inst in self._installations.values()
        )

        if has_running:
            return ServiceStatus.RUNNING

        return ServiceStatus.STOPPED

    def is_installed(self) -> bool:
        """Check if any Discord version is installed."""
        self.detect_all()
        return any(
            inst.method != InstallMethod.NOT_INSTALLED
            for inst in self._installations.values()
        )

    # =========================================================================
    # Detection methods
    # =========================================================================

    def detect_all(self) -> dict[DiscordVersion, DiscordInstallation]:
        """
        Detect all Discord installations.

        Returns:
            Dictionary of detected installations
        """
        for version in DiscordVersion:
            self._installations[version] = self._detect_version(version)

        self._webcord = self._detect_webcord()

        return self._installations.copy()

    def _detect_version(self, version: DiscordVersion) -> DiscordInstallation:
        """
        Detect a specific Discord version.

        Args:
            version: Discord version to detect

        Returns:
            DiscordInstallation with detection results
        """
        installation = DiscordInstallation(
            version=version,
            method=InstallMethod.NOT_INSTALLED,
            config_dir=DISCORD_CONFIG_DIRS.get(version.value),
            cache_dir=DISCORD_CACHE_DIRS.get(version.value),
        )

        # Check for DEB installation
        deb_name = DEB_DISCORD_NAMES.get(version.value)
        if deb_name and self._is_deb_installed(deb_name):
            installation.method = InstallMethod.DEB
            installation.path = f"/usr/share/{deb_name}"
            installation.binary_path = self._find_binary(version)

        # Check for Snap installation
        elif self._is_snap_installed(version):
            installation.method = InstallMethod.SNAP
            snap_name = SNAP_DISCORD_NAMES.get(version.value)
            installation.path = f"/snap/{snap_name}/current"
            installation.binary_path = f"/snap/bin/{snap_name}"

        # Check for Flatpak installation
        elif self._is_flatpak_installed(version):
            installation.method = InstallMethod.FLATPAK
            flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
            installation.path = f"flatpak:{flatpak_id}"
            installation.binary_path = f"flatpak run {flatpak_id}"

        # Check for tarball/manual installation
        elif self._find_binary(version):
            installation.method = InstallMethod.TARBALL
            installation.binary_path = self._find_binary(version)

        # Check running status
        installation.is_running = self._is_discord_running(version)

        # Check cache
        if installation.cache_dir and installation.cache_dir.exists():
            installation.has_cache = True
            installation.cache_size_mb = self._get_dir_size_mb(installation.cache_dir)

        return installation

    def _is_deb_installed(self, package_name: str) -> bool:
        """Check if a DEB package is installed."""
        result = self._shell.run(
            ["dpkg", "-s", package_name],
            timeout=10
        )
        return result.success and "Status: install ok installed" in result.stdout

    def _is_snap_installed(self, version: DiscordVersion) -> bool:
        """Check if Discord is installed via Snap."""
        snap_name = SNAP_DISCORD_NAMES.get(version.value)
        if not snap_name:
            return False

        result = self._shell.run(
            ["snap", "list", snap_name],
            timeout=10
        )
        return result.success

    def _is_flatpak_installed(self, version: DiscordVersion) -> bool:
        """Check if Discord is installed via Flatpak."""
        flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
        if not flatpak_id:
            return False

        result = self._shell.run(
            ["flatpak", "info", flatpak_id],
            timeout=10
        )
        return result.success

    def _find_binary(self, version: DiscordVersion) -> Optional[str]:
        """Find Discord binary in PATH."""
        binaries = DISCORD_BINARIES.get(version.value, [])
        for binary in binaries:
            path = self._shell.get_command_path(binary)
            if path:
                return path
        return None

    def _is_discord_running(self, version: DiscordVersion) -> bool:
        """Check if Discord version is running."""
        binaries = DISCORD_BINARIES.get(version.value, [])
        for binary in binaries:
            result = self._shell.run(
                ["pgrep", "-f", binary],
                timeout=5
            )
            if result.success and result.stdout.strip():
                return True
        return False

    def _detect_webcord(self) -> WebCordInstallation:
        """Detect WebCord installation."""
        webcord = WebCordInstallation()

        # Check Flatpak
        result = self._shell.run(
            ["flatpak", "info", "io.github.nickvision.webcord"],
            timeout=10
        )
        if result.success:
            webcord.installed = True
            webcord.method = InstallMethod.FLATPAK
            webcord.path = "flatpak:io.github.nickvision.webcord"

        # Check for AppImage or binary
        webcord_paths = [
            Path.home() / "Applications" / "WebCord.AppImage",
            Path.home() / ".local" / "bin" / "webcord",
            Path("/usr/bin/webcord"),
            Path("/usr/local/bin/webcord"),
        ]

        for path in webcord_paths:
            if path.exists():
                webcord.installed = True
                webcord.method = InstallMethod.APPIMAGE if "AppImage" in str(path) else InstallMethod.UNKNOWN
                webcord.path = str(path)
                break

        # Check if running
        result = self._shell.run(["pgrep", "-f", "webcord"], timeout=5)
        webcord.is_running = result.success and bool(result.stdout.strip())

        return webcord

    def _get_dir_size_mb(self, path: Path) -> float:
        """Get directory size in MB."""
        try:
            total = 0
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
            return total / (1024 * 1024)
        except Exception:
            return 0.0

    # =========================================================================
    # Repair methods
    # =========================================================================

    def repair_discord(self, version: DiscordVersion = DiscordVersion.STABLE,
                       clear_cache: bool = True,
                       reinstall: bool = False) -> RepairResult:
        """
        Repair Discord installation.

        Args:
            version: Discord version to repair
            clear_cache: Whether to clear cache
            reinstall: Whether to reinstall Discord

        Returns:
            RepairResult with operation details
        """
        self._logger.info(f"Repairing Discord {version.value}")
        errors = []
        cache_cleared = 0.0

        # Kill Discord if running
        if self._is_discord_running(version):
            self._logger.info("Stopping Discord...")
            self._kill_discord_version(version)

        # Clear cache
        if clear_cache:
            cache_result = self.clear_cache(version)
            if cache_result.success:
                cache_cleared = cache_result.cache_cleared_mb
            else:
                errors.extend(cache_result.errors)

        # Clear config corruption markers
        config_dir = DISCORD_CONFIG_DIRS.get(version.value)
        if config_dir and config_dir.exists():
            # Remove potentially corrupted files
            corrupt_files = [
                config_dir / "GPUCache",
                config_dir / "Code Cache",
                config_dir / "Crashpad",
            ]
            for cf in corrupt_files:
                if cf.exists():
                    try:
                        shutil.rmtree(cf)
                        self._logger.info(f"Removed: {cf}")
                    except Exception as e:
                        errors.append(f"Failed to remove {cf}: {e}")

        # Reinstall if requested
        if reinstall:
            installation = self._detect_version(version)
            if installation.method == InstallMethod.DEB:
                reinstall_result = self._reinstall_deb(version)
                if not reinstall_result:
                    errors.append("Failed to reinstall Discord DEB package")
            elif installation.method == InstallMethod.FLATPAK:
                reinstall_result = self._reinstall_flatpak(version)
                if not reinstall_result:
                    errors.append("Failed to reinstall Discord Flatpak")
            elif installation.method == InstallMethod.SNAP:
                reinstall_result = self._reinstall_snap(version)
                if not reinstall_result:
                    errors.append("Failed to reinstall Discord Snap")

        # Update config
        self._config.last_repair_date = datetime.now().isoformat()
        self._save_config()

        success = len(errors) == 0
        message = "Repair completed successfully" if success else f"Repair completed with {len(errors)} error(s)"

        return RepairResult(
            success=success,
            message=message,
            cache_cleared_mb=cache_cleared,
            errors=errors,
        )

    def clear_cache(self, version: DiscordVersion = DiscordVersion.STABLE) -> RepairResult:
        """
        Clear Discord cache.

        Args:
            version: Discord version to clear cache for

        Returns:
            RepairResult with details
        """
        self._logger.info(f"Clearing cache for Discord {version.value}")
        errors = []
        total_cleared = 0.0

        # Clear cache directory
        cache_dir = DISCORD_CACHE_DIRS.get(version.value)
        if cache_dir and cache_dir.exists():
            size = self._get_dir_size_mb(cache_dir)
            try:
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                total_cleared += size
                self._logger.info(f"Cleared {size:.1f} MB from {cache_dir}")
            except Exception as e:
                errors.append(f"Failed to clear cache dir: {e}")

        # Clear config cache subdirectories
        config_dir = DISCORD_CONFIG_DIRS.get(version.value)
        if config_dir and config_dir.exists():
            cache_subdirs = ["Cache", "GPUCache", "Code Cache", "blob_storage"]
            for subdir in cache_subdirs:
                subdir_path = config_dir / subdir
                if subdir_path.exists():
                    size = self._get_dir_size_mb(subdir_path)
                    try:
                        shutil.rmtree(subdir_path)
                        total_cleared += size
                        self._logger.info(f"Cleared {size:.1f} MB from {subdir_path}")
                    except Exception as e:
                        errors.append(f"Failed to clear {subdir}: {e}")

        success = len(errors) == 0
        message = f"Cleared {total_cleared:.1f} MB of cache" if success else "Cache clearing had errors"

        return RepairResult(
            success=success,
            message=message,
            cache_cleared_mb=total_cleared,
            errors=errors,
        )

    def clear_all_cache(self) -> RepairResult:
        """Clear cache for all Discord versions."""
        total_cleared = 0.0
        all_errors = []

        for version in DiscordVersion:
            result = self.clear_cache(version)
            total_cleared += result.cache_cleared_mb
            all_errors.extend(result.errors)

        success = len(all_errors) == 0
        return RepairResult(
            success=success,
            message=f"Cleared {total_cleared:.1f} MB total",
            cache_cleared_mb=total_cleared,
            errors=all_errors,
        )

    # =========================================================================
    # Installation methods
    # =========================================================================

    def install_discord(self, version: DiscordVersion = DiscordVersion.STABLE,
                        method: InstallMethod = InstallMethod.DEB) -> bool:
        """
        Install Discord.

        Args:
            version: Discord version to install
            method: Installation method (deb, flatpak, snap)

        Returns:
            True if installation successful
        """
        self._logger.info(f"Installing Discord {version.value} via {method.value}")

        if method == InstallMethod.DEB:
            return self._install_deb(version)
        elif method == InstallMethod.FLATPAK:
            return self._install_flatpak(version)
        elif method == InstallMethod.SNAP:
            return self._install_snap(version)
        else:
            self._logger.error(f"Unsupported installation method: {method}")
            return False

    def _install_deb(self, version: DiscordVersion) -> bool:
        """Install Discord via DEB package."""
        url = DISCORD_DOWNLOAD_URLS.get(version.value)
        if not url:
            return False

        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                deb_path = Path(tmpdir) / f"discord-{version.value}.deb"

                # Download DEB
                self._logger.info(f"Downloading Discord {version.value}...")
                result = self._shell.run(
                    ["wget", "-q", "-O", str(deb_path), url],
                    timeout=120
                )
                if not result.success:
                    self._logger.error(f"Download failed: {result.stderr}")
                    return False

                # Install DEB
                self._logger.info("Installing DEB package...")
                result = self._run_privileged(
                    ["dpkg", "-i", str(deb_path)],
                    timeout=60
                )

                # Fix dependencies if needed
                if not result.success:
                    self._logger.info("Fixing dependencies...")
                    self._run_privileged(
                        ["apt-get", "install", "-f", "-y"],
                        timeout=120
                    )

                self._logger.info(f"Discord {version.value} installed successfully")
                return True

        except Exception as e:
            self._logger.exception(f"Installation failed: {e}")
            return False

    def _install_flatpak(self, version: DiscordVersion) -> bool:
        """Install Discord via Flatpak."""
        flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
        if not flatpak_id:
            return False

        # Ensure Flatpak is installed
        if not self._shell.command_exists("flatpak"):
            self._logger.error("Flatpak is not installed")
            return False

        # Add Flathub if not present
        self._shell.run(
            ["flatpak", "remote-add", "--if-not-exists", "flathub",
             "https://flathub.org/repo/flathub.flatpakrepo"],
            timeout=30
        )

        # Install Discord
        result = self._shell.run(
            ["flatpak", "install", "-y", "flathub", flatpak_id],
            timeout=300
        )

        if result.success:
            self._logger.info(f"Discord {version.value} installed via Flatpak")
        else:
            self._logger.error(f"Flatpak install failed: {result.stderr}")

        return result.success

    def _install_snap(self, version: DiscordVersion) -> bool:
        """Install Discord via Snap."""
        snap_name = SNAP_DISCORD_NAMES.get(version.value)
        if not snap_name:
            return False

        # Ensure Snap is installed
        if not self._shell.command_exists("snap"):
            self._logger.error("Snap is not installed")
            return False

        result = self._run_privileged(
            ["snap", "install", snap_name],
            timeout=300
        )

        if result.success:
            self._logger.info(f"Discord {version.value} installed via Snap")
        else:
            self._logger.error(f"Snap install failed: {result.stderr}")

        return result.success

    def _reinstall_deb(self, version: DiscordVersion) -> bool:
        """Reinstall Discord DEB package."""
        deb_name = DEB_DISCORD_NAMES.get(version.value)
        if not deb_name:
            return False

        # Remove existing
        self._run_privileged(["dpkg", "-r", deb_name], timeout=30)

        # Install fresh
        return self._install_deb(version)

    def _reinstall_flatpak(self, version: DiscordVersion) -> bool:
        """Reinstall Discord Flatpak."""
        flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
        if not flatpak_id:
            return False

        # Remove existing
        self._shell.run(["flatpak", "uninstall", "-y", flatpak_id], timeout=60)

        # Install fresh
        return self._install_flatpak(version)

    def _reinstall_snap(self, version: DiscordVersion) -> bool:
        """Reinstall Discord Snap."""
        snap_name = SNAP_DISCORD_NAMES.get(version.value)
        if not snap_name:
            return False

        # Remove existing
        self._run_privileged(["snap", "remove", snap_name], timeout=60)

        # Install fresh
        return self._install_snap(version)

    def uninstall_discord(self, version: DiscordVersion) -> bool:
        """
        Uninstall Discord.

        Args:
            version: Discord version to uninstall

        Returns:
            True if uninstallation successful
        """
        installation = self._detect_version(version)

        if installation.method == InstallMethod.NOT_INSTALLED:
            self._logger.info(f"Discord {version.value} is not installed")
            return True

        self._logger.info(f"Uninstalling Discord {version.value}")

        # Kill if running
        if installation.is_running:
            self._kill_discord_version(version)

        if installation.method == InstallMethod.DEB:
            deb_name = DEB_DISCORD_NAMES.get(version.value)
            result = self._run_privileged(["dpkg", "-r", deb_name], timeout=30)
        elif installation.method == InstallMethod.FLATPAK:
            flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
            result = self._shell.run(["flatpak", "uninstall", "-y", flatpak_id], timeout=60)
        elif installation.method == InstallMethod.SNAP:
            snap_name = SNAP_DISCORD_NAMES.get(version.value)
            result = self._run_privileged(["snap", "remove", snap_name], timeout=60)
        else:
            self._logger.warning(f"Cannot uninstall {installation.method.value} installation")
            return False

        return result.success

    # =========================================================================
    # WebCord methods
    # =========================================================================

    def install_webcord(self, method: InstallMethod = InstallMethod.FLATPAK,
                        create_shortcut: bool = True) -> bool:
        """
        Install WebCord.

        Args:
            method: Installation method (flatpak recommended)
            create_shortcut: Whether to create desktop shortcut

        Returns:
            True if installation successful
        """
        self._logger.info(f"Installing WebCord via {method.value}")

        if method == InstallMethod.FLATPAK:
            # Ensure Flatpak is installed
            if not self._shell.command_exists("flatpak"):
                self._logger.error("Flatpak is not installed")
                return False

            # Add Flathub
            self._shell.run(
                ["flatpak", "remote-add", "--if-not-exists", "flathub",
                 "https://flathub.org/repo/flathub.flatpakrepo"],
                timeout=30
            )

            # Try different WebCord Flatpak IDs
            webcord_ids = [
                "io.github.nickvision.webcord",
                "io.github.nickvision.Webcord",
                "org.nickvision.webcord",
            ]

            for flatpak_id in webcord_ids:
                result = self._shell.run(
                    ["flatpak", "install", "-y", "flathub", flatpak_id],
                    timeout=300
                )
                if result.success:
                    self._logger.info("WebCord installed via Flatpak")
                    return True

            self._logger.error("Failed to install WebCord via Flatpak")
            return False

        else:
            self._logger.error(f"Unsupported WebCord installation method: {method}")
            return False

    def uninstall_webcord(self) -> bool:
        """Uninstall WebCord."""
        webcord = self._detect_webcord()

        if not webcord.installed:
            return True

        if webcord.method == InstallMethod.FLATPAK:
            result = self._shell.run(
                ["flatpak", "uninstall", "-y", "io.github.nickvision.webcord"],
                timeout=60
            )
            return result.success
        elif webcord.method == InstallMethod.APPIMAGE and webcord.path:
            try:
                Path(webcord.path).unlink()
                return True
            except Exception as e:
                self._logger.error(f"Failed to remove WebCord: {e}")
                return False

        return False

    # =========================================================================
    # Launch/kill methods
    # =========================================================================

    def launch_discord(self, version: DiscordVersion = DiscordVersion.STABLE) -> bool:
        """
        Launch Discord.

        Args:
            version: Discord version to launch

        Returns:
            True if launched successfully
        """
        installation = self._detect_version(version)

        if installation.method == InstallMethod.NOT_INSTALLED:
            self._logger.error(f"Discord {version.value} is not installed")
            return False

        if installation.is_running:
            self._logger.info(f"Discord {version.value} is already running")
            return True

        self._logger.info(f"Launching Discord {version.value}")

        if installation.method == InstallMethod.FLATPAK:
            flatpak_id = FLATPAK_DISCORD_IDS.get(version.value)
            cmd = ["flatpak", "run", flatpak_id]
        elif installation.binary_path:
            cmd = [installation.binary_path]
        else:
            self._logger.error("Cannot find Discord binary")
            return False

        # Launch in background
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception as e:
            self._logger.error(f"Failed to launch Discord: {e}")
            return False

    def launch_webcord(self) -> bool:
        """Launch WebCord."""
        webcord = self._detect_webcord()

        if not webcord.installed:
            self._logger.error("WebCord is not installed")
            return False

        if webcord.is_running:
            self._logger.info("WebCord is already running")
            return True

        try:
            if webcord.method == InstallMethod.FLATPAK:
                subprocess.Popen(
                    ["flatpak", "run", "io.github.nickvision.webcord"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            elif webcord.path:
                subprocess.Popen(
                    [webcord.path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            return True
        except Exception as e:
            self._logger.error(f"Failed to launch WebCord: {e}")
            return False

    def kill_discord(self, version: Optional[DiscordVersion] = None) -> bool:
        """
        Kill Discord process(es).

        Args:
            version: Specific version to kill, or None for all

        Returns:
            True if killed successfully
        """
        if version:
            return self._kill_discord_version(version)

        # Kill all versions
        success = True
        for v in DiscordVersion:
            if not self._kill_discord_version(v):
                success = False
        return success

    def _kill_discord_version(self, version: DiscordVersion) -> bool:
        """Kill specific Discord version."""
        binaries = DISCORD_BINARIES.get(version.value, [])

        for binary in binaries:
            self._shell.run(["pkill", "-f", binary], timeout=5)

        # Give it time to close
        import time
        time.sleep(1)

        return not self._is_discord_running(version)

    # =========================================================================
    # Status methods
    # =========================================================================

    def get_config(self) -> DiscordConfig:
        """Get current configuration."""
        return self._config

    def get_installations(self) -> dict[DiscordVersion, DiscordInstallation]:
        """Get all detected installations."""
        self.detect_all()
        return self._installations.copy()

    def get_installation(self, version: DiscordVersion) -> DiscordInstallation:
        """Get specific installation info."""
        return self._detect_version(version)

    def get_webcord(self) -> WebCordInstallation:
        """Get WebCord installation info."""
        return self._detect_webcord()

    def get_total_cache_size(self) -> float:
        """Get total cache size for all Discord versions in MB."""
        total = 0.0
        for version in DiscordVersion:
            cache_dir = DISCORD_CACHE_DIRS.get(version.value)
            if cache_dir and cache_dir.exists():
                total += self._get_dir_size_mb(cache_dir)

            config_dir = DISCORD_CONFIG_DIRS.get(version.value)
            if config_dir and config_dir.exists():
                for subdir in ["Cache", "GPUCache", "Code Cache"]:
                    subdir_path = config_dir / subdir
                    if subdir_path.exists():
                        total += self._get_dir_size_mb(subdir_path)

        return total

    def set_preferred_version(self, version: str) -> None:
        """Set preferred Discord version."""
        self._config.preferred_version = version
        self._save_config()

    def set_auto_clear_cache(self, enabled: bool) -> None:
        """Set auto clear cache option."""
        self._config.auto_clear_cache = enabled
        self._save_config()


# ============================================================================
# Convenience functions
# ============================================================================

_discord_service: Optional[DiscordService] = None


def get_discord_service() -> DiscordService:
    """Get the global Discord service instance."""
    global _discord_service
    if _discord_service is None:
        _discord_service = DiscordService()
    return _discord_service


if __name__ == "__main__":
    # Test the Discord service
    print("=" * 50)
    print("Discord Service Test")
    print("=" * 50)

    service = DiscordService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print("\nDetecting Discord installations...")
    installations = service.detect_all()

    for version, inst in installations.items():
        print(f"\n{version.value.upper()}:")
        print(f"  Method: {inst.method.value}")
        print(f"  Path: {inst.path or 'N/A'}")
        print(f"  Binary: {inst.binary_path or 'N/A'}")
        print(f"  Running: {inst.is_running}")
        print(f"  Has Cache: {inst.has_cache}")
        if inst.has_cache:
            print(f"  Cache Size: {inst.cache_size_mb:.1f} MB")

    webcord = service.get_webcord()
    print(f"\nWebCord:")
    print(f"  Installed: {webcord.installed}")
    print(f"  Method: {webcord.method.value}")
    print(f"  Running: {webcord.is_running}")

    print(f"\nTotal cache size: {service.get_total_cache_size():.1f} MB")
    print(f"Service status: {service.status().value}")

    print("\nTest completed!")
