"""
Tests for the configuration manager module.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.core.config import (
    ConfigManager,
    AppConfig,
    DNSConfig,
    WireGuardConfig,
    ZapretConfig,
    ByeDPIConfig,
    Theme,
    Language,
)


class TestAppConfig:
    """Tests for AppConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AppConfig()
        assert config.version == "1.0.0"
        assert config.theme == Theme.SYSTEM
        assert config.language == Language.TR
        assert config.auto_dns is True
        assert config.start_minimized is False

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AppConfig(
            theme=Theme.DARK,
            language=Language.EN,
            auto_dns=False,
        )
        assert config.theme == Theme.DARK
        assert config.language == Language.EN
        assert config.auto_dns is False


class TestDNSConfig:
    """Tests for DNSConfig dataclass."""

    def test_default_values(self):
        """Test default DNS configuration."""
        config = DNSConfig()
        assert config.enabled is False
        assert config.primary == "8.8.8.8"
        assert config.secondary == "8.8.4.4"
        assert config.doh_enabled is False

    def test_custom_dns(self):
        """Test custom DNS settings."""
        config = DNSConfig(
            enabled=True,
            primary="1.1.1.1",
            secondary="1.0.0.1",
            doh_enabled=True,
            doh_url="https://cloudflare-dns.com/dns-query",
        )
        assert config.enabled is True
        assert config.primary == "1.1.1.1"
        assert config.doh_url == "https://cloudflare-dns.com/dns-query"


class TestWireGuardConfig:
    """Tests for WireGuardConfig dataclass."""

    def test_default_values(self):
        """Test default WireGuard configuration."""
        config = WireGuardConfig()
        assert config.enabled is False
        assert config.config_path is None
        assert config.split_tunnel is True
        assert config.allowed_apps == []

    def test_with_apps(self):
        """Test WireGuard config with allowed apps."""
        config = WireGuardConfig(
            enabled=True,
            split_tunnel=True,
            allowed_apps=["/usr/bin/discord", "/usr/bin/firefox"],
        )
        assert len(config.allowed_apps) == 2
        assert "/usr/bin/discord" in config.allowed_apps


class TestZapretConfig:
    """Tests for ZapretConfig dataclass."""

    def test_default_values(self):
        """Test default Zapret configuration."""
        config = ZapretConfig()
        assert config.enabled is False
        assert config.mode == "nfqws"
        assert config.preset == "turkey_discord"

    def test_custom_args(self):
        """Test Zapret with custom arguments."""
        config = ZapretConfig(
            enabled=True,
            mode="tpws",
            custom_args="--split-pos=2",
        )
        assert config.mode == "tpws"
        assert config.custom_args == "--split-pos=2"


class TestByeDPIConfig:
    """Tests for ByeDPIConfig dataclass."""

    def test_default_values(self):
        """Test default ByeDPI configuration."""
        config = ByeDPIConfig()
        assert config.enabled is False
        assert config.port == 1080
        assert config.strategy == "disorder"

    def test_custom_port(self):
        """Test ByeDPI with custom port."""
        config = ByeDPIConfig(port=8080, strategy="split")
        assert config.port == 8080
        assert config.strategy == "split"


class TestConfigManager:
    """Tests for ConfigManager class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create a ConfigManager with temporary directory."""
        with patch.object(ConfigManager, '_get_config_dir', return_value=temp_config_dir):
            manager = ConfigManager.__new__(ConfigManager)
            manager._config_dir = temp_config_dir
            manager._config_file = temp_config_dir / "config.json"
            manager._config = AppConfig()
            return manager

    def test_config_dir_creation(self, temp_config_dir):
        """Test that config directory is created."""
        config_dir = temp_config_dir / "splitwire"
        with patch.object(ConfigManager, '_get_config_dir', return_value=config_dir):
            manager = ConfigManager.__new__(ConfigManager)
            manager._config_dir = config_dir
            manager._config_dir.mkdir(parents=True, exist_ok=True)
            assert config_dir.exists()

    def test_save_and_load_config(self, config_manager, temp_config_dir):
        """Test saving and loading configuration."""
        # Modify config
        config_manager._config.theme = Theme.DARK
        config_manager._config.language = Language.EN

        # Save to file
        config_file = temp_config_dir / "config.json"
        config_dict = {
            "version": config_manager._config.version,
            "theme": config_manager._config.theme.value,
            "language": config_manager._config.language.value,
            "auto_dns": config_manager._config.auto_dns,
            "start_minimized": config_manager._config.start_minimized,
        }
        with open(config_file, "w") as f:
            json.dump(config_dict, f)

        # Verify file was created
        assert config_file.exists()

        # Load and verify
        with open(config_file) as f:
            loaded = json.load(f)
        assert loaded["theme"] == "dark"
        assert loaded["language"] == "en"

    def test_default_config_creation(self, temp_config_dir):
        """Test that default config is created when none exists."""
        config_file = temp_config_dir / "config.json"
        assert not config_file.exists()

        # Create default config
        default_config = AppConfig()
        config_dict = {
            "version": default_config.version,
            "theme": default_config.theme.value,
            "language": default_config.language.value,
        }
        with open(config_file, "w") as f:
            json.dump(config_dict, f)

        assert config_file.exists()


class TestThemeEnum:
    """Tests for Theme enumeration."""

    def test_theme_values(self):
        """Test all theme values exist."""
        assert Theme.LIGHT.value == "light"
        assert Theme.DARK.value == "dark"
        assert Theme.SYSTEM.value == "system"

    def test_theme_from_string(self):
        """Test creating theme from string."""
        assert Theme("light") == Theme.LIGHT
        assert Theme("dark") == Theme.DARK


class TestLanguageEnum:
    """Tests for Language enumeration."""

    def test_language_values(self):
        """Test all language values exist."""
        assert Language.TR.value == "tr"
        assert Language.EN.value == "en"
        assert Language.RU.value == "ru"
        assert Language.ES.value == "es"

    def test_language_from_string(self):
        """Test creating language from string."""
        assert Language("tr") == Language.TR
        assert Language("en") == Language.EN
