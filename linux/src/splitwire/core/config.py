"""
Configuration manager for SplitWire-Turkey Linux.

Handles application settings using XDG Base Directory specification.
Config is stored in ~/.config/splitwire/config.json
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any
from enum import Enum


class Theme(Enum):
    """Application theme."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class Language(Enum):
    """Supported languages."""
    TURKISH = "tr"
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"


@dataclass
class DNSConfig:
    """DNS configuration."""
    enabled: bool = False
    primary: str = "1.1.1.1"
    secondary: str = "1.0.0.1"
    doh_enabled: bool = False
    doh_url: str = "https://cloudflare-dns.com/dns-query"


@dataclass
class WireGuardConfig:
    """WireGuard/VPN configuration."""
    config_path: str = ""
    auto_connect: bool = False
    split_tunnel_enabled: bool = True
    allowed_apps: list[str] = field(default_factory=list)
    excluded_apps: list[str] = field(default_factory=list)
    custom_apps: list[str] = field(default_factory=list)  # User-added custom app paths
    enabled_known_apps: dict[str, bool] = field(default_factory=dict)  # Which known apps are enabled
    kill_switch: bool = False
    include_browsers: bool = False
    refresh_timer_enabled: bool = False


@dataclass
class ZapretConfig:
    """Zapret DPI bypass configuration."""
    enabled: bool = False
    mode: str = "nfqws"  # nfqws or tpws
    strategy: str = "default"
    custom_args: str = ""
    auto_start: bool = False


@dataclass
class ByeDPIConfig:
    """ByeDPI/ciadpi proxy configuration."""
    enabled: bool = False
    port: int = 10080
    strategy: str = "disorder"
    custom_args: str = ""
    proxy_apps: list[str] = field(default_factory=list)


@dataclass
class AppConfig:
    """Main application configuration."""
    # General
    theme: str = Theme.SYSTEM.value
    language: str = Language.ENGLISH.value
    minimize_to_tray: bool = True
    start_minimized: bool = False
    auto_start: bool = False
    check_updates: bool = True

    # Feature configs
    dns: DNSConfig = field(default_factory=DNSConfig)
    wireguard: WireGuardConfig = field(default_factory=WireGuardConfig)
    zapret: ZapretConfig = field(default_factory=ZapretConfig)
    byedpi: ByeDPIConfig = field(default_factory=ByeDPIConfig)

    # State (not saved)
    first_run: bool = True
    version: str = "1.0.0"


class ConfigManager:
    """
    Manages application configuration.

    Uses XDG Base Directory specification:
    - Config: ~/.config/splitwire/
    - Data: ~/.local/share/splitwire/
    - Cache: ~/.cache/splitwire/
    """

    APP_NAME = "splitwire"
    CONFIG_FILE = "config.json"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_dir: Override config directory (for testing)
        """
        self._config_dir = config_dir or self._get_xdg_config_dir()
        self._data_dir = self._get_xdg_data_dir()
        self._cache_dir = self._get_xdg_cache_dir()
        self._config: Optional[AppConfig] = None
        self._config_file = self._config_dir / self.CONFIG_FILE

        # Ensure directories exist
        self._ensure_directories()

    def _get_xdg_config_dir(self) -> Path:
        """Get XDG config directory."""
        xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg_config:
            return Path(xdg_config) / self.APP_NAME
        return Path.home() / ".config" / self.APP_NAME

    def _get_xdg_data_dir(self) -> Path:
        """Get XDG data directory."""
        xdg_data = os.environ.get("XDG_DATA_HOME", "")
        if xdg_data:
            return Path(xdg_data) / self.APP_NAME
        return Path.home() / ".local" / "share" / self.APP_NAME

    def _get_xdg_cache_dir(self) -> Path:
        """Get XDG cache directory."""
        xdg_cache = os.environ.get("XDG_CACHE_HOME", "")
        if xdg_cache:
            return Path(xdg_cache) / self.APP_NAME
        return Path.home() / ".cache" / self.APP_NAME

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self._config_dir, self._data_dir, self._cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def config_dir(self) -> Path:
        """Get config directory path."""
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return self._data_dir

    @property
    def cache_dir(self) -> Path:
        """Get cache directory path."""
        return self._cache_dir

    @property
    def config(self) -> AppConfig:
        """Get current configuration (loads if needed)."""
        if self._config is None:
            self.load()
        return self._config

    def load(self) -> AppConfig:
        """
        Load configuration from file.

        Returns:
            Loaded configuration (or defaults if file doesn't exist)
        """
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = self._dict_to_config(data)
                self._config.first_run = False
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Config file corrupted, use defaults
                print(f"Warning: Config file corrupted, using defaults: {e}")
                self._config = AppConfig()
        else:
            self._config = AppConfig()

        return self._config

    def save(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if save succeeded
        """
        if self._config is None:
            self._config = AppConfig()

        try:
            data = self._config_to_dict(self._config)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def reset(self) -> AppConfig:
        """
        Reset configuration to defaults.

        Returns:
            New default configuration
        """
        self._config = AppConfig()
        self.save()
        return self._config

    def _config_to_dict(self, config: AppConfig) -> dict:
        """Convert AppConfig to dictionary for JSON serialization."""
        return {
            "theme": config.theme,
            "language": config.language,
            "minimize_to_tray": config.minimize_to_tray,
            "start_minimized": config.start_minimized,
            "auto_start": config.auto_start,
            "check_updates": config.check_updates,
            "version": config.version,
            "dns": asdict(config.dns),
            "wireguard": asdict(config.wireguard),
            "zapret": asdict(config.zapret),
            "byedpi": asdict(config.byedpi),
        }

    def _dict_to_config(self, data: dict) -> AppConfig:
        """Convert dictionary to AppConfig."""
        config = AppConfig()

        # Simple fields
        config.theme = data.get("theme", config.theme)
        config.language = data.get("language", config.language)
        config.minimize_to_tray = data.get("minimize_to_tray", config.minimize_to_tray)
        config.start_minimized = data.get("start_minimized", config.start_minimized)
        config.auto_start = data.get("auto_start", config.auto_start)
        config.check_updates = data.get("check_updates", config.check_updates)
        config.version = data.get("version", config.version)

        # Nested configs
        if "dns" in data:
            config.dns = DNSConfig(**data["dns"])
        if "wireguard" in data:
            config.wireguard = WireGuardConfig(**data["wireguard"])
        if "zapret" in data:
            config.zapret = ZapretConfig(**data["zapret"])
        if "byedpi" in data:
            config.byedpi = ByeDPIConfig(**data["byedpi"])

        return config

    # Convenience methods

    def get_wireguard_configs_dir(self) -> Path:
        """Get directory for WireGuard configuration files."""
        wg_dir = self._data_dir / "wireguard"
        wg_dir.mkdir(parents=True, exist_ok=True)
        return wg_dir

    def get_zapret_dir(self) -> Path:
        """Get directory for Zapret installation."""
        zapret_dir = self._data_dir / "zapret"
        zapret_dir.mkdir(parents=True, exist_ok=True)
        return zapret_dir

    def get_logs_dir(self) -> Path:
        """Get directory for log files."""
        logs_dir = self._cache_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    def get_backups_dir(self) -> Path:
        """Get directory for backup files."""
        backups_dir = self._data_dir / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        return backups_dir


# Global instance for convenience
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().config


def save_config() -> bool:
    """Save the current configuration."""
    return get_config_manager().save()


if __name__ == "__main__":
    # Test the config manager
    manager = ConfigManager()

    print("=" * 50)
    print("ConfigManager Test")
    print("=" * 50)
    print(f"Config dir: {manager.config_dir}")
    print(f"Data dir: {manager.data_dir}")
    print(f"Cache dir: {manager.cache_dir}")
    print(f"Config file: {manager._config_file}")

    # Load config
    config = manager.load()
    print(f"\nLoaded config:")
    print(f"  Theme: {config.theme}")
    print(f"  Language: {config.language}")
    print(f"  First run: {config.first_run}")
    print(f"  DNS enabled: {config.dns.enabled}")
    print(f"  WireGuard split tunnel: {config.wireguard.split_tunnel_enabled}")

    # Modify and save
    config.theme = Theme.DARK.value
    manager.save()
    print("\nConfig saved!")

    # Reload to verify
    manager2 = ConfigManager()
    config2 = manager2.load()
    print(f"Reloaded theme: {config2.theme}")
