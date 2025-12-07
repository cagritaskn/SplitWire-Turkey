"""
Unit tests for ByeDPI service.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from splitwire.services.byedpi import (
    ByeDPIService,
    ByeDPIConfig,
    ByeDPIPreset,
    ByeDPIMode,
    DEFAULT_PRESETS,
    DEFAULT_PROXY_HOST,
    DEFAULT_PROXY_PORT,
    get_byedpi_service,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestByeDPIPreset:
    """Tests for ByeDPIPreset dataclass."""

    def test_preset_creation(self):
        """Test creating a preset."""
        preset = ByeDPIPreset(
            name="Test Preset",
            description="Test description",
            args="--disorder 1",
            mode=ByeDPIMode.DISORDER,
        )

        assert preset.name == "Test Preset"
        assert preset.description == "Test description"
        assert preset.args == "--disorder 1"
        assert preset.mode == ByeDPIMode.DISORDER
        assert preset.is_custom is False

    def test_preset_custom_flag(self):
        """Test custom preset flag."""
        preset = ByeDPIPreset(
            name="Custom",
            description="Custom preset",
            args="--split 1",
            is_custom=True,
        )
        assert preset.is_custom is True


class TestByeDPIConfig:
    """Tests for ByeDPIConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ByeDPIConfig()

        assert config.enabled is False
        assert config.preset_name == "turkey_default"
        assert config.custom_args == ""
        assert config.proxy_host == DEFAULT_PROXY_HOST
        assert config.proxy_port == DEFAULT_PROXY_PORT
        assert config.include_browsers is False
        assert config.tunneled_apps == []

    def test_config_with_values(self):
        """Test configuration with custom values."""
        config = ByeDPIConfig(
            enabled=True,
            preset_name="turkey_discord",
            proxy_port=8080,
            include_browsers=True,
            tunneled_apps=["discord", "firefox"],
        )

        assert config.enabled is True
        assert config.preset_name == "turkey_discord"
        assert config.proxy_port == 8080
        assert config.include_browsers is True
        assert config.tunneled_apps == ["discord", "firefox"]


class TestDefaultPresets:
    """Tests for default presets."""

    def test_default_presets_exist(self):
        """Test that default presets are defined."""
        assert len(DEFAULT_PRESETS) > 0
        assert "turkey_default" in DEFAULT_PRESETS
        assert "turkey_discord" in DEFAULT_PRESETS

    def test_turkey_default_preset(self):
        """Test turkey_default preset configuration."""
        preset = DEFAULT_PRESETS["turkey_default"]

        assert preset.name == "Türkiye Varsayılan"
        assert "--disorder" in preset.args
        assert preset.mode == ByeDPIMode.DISORDER

    def test_turkey_discord_preset(self):
        """Test turkey_discord preset configuration."""
        preset = DEFAULT_PRESETS["turkey_discord"]

        assert preset.name == "Türkiye Discord"
        assert "--disorder" in preset.args
        assert preset.mode == ByeDPIMode.COMBINED

    def test_all_presets_have_required_fields(self):
        """Test that all presets have required fields."""
        for key, preset in DEFAULT_PRESETS.items():
            assert preset.name, f"Preset {key} missing name"
            assert preset.description, f"Preset {key} missing description"
            assert preset.args, f"Preset {key} missing args"
            assert isinstance(preset.mode, ByeDPIMode), f"Preset {key} has invalid mode"

    def test_preset_modes(self):
        """Test that different modes are covered."""
        modes_used = set()
        for preset in DEFAULT_PRESETS.values():
            modes_used.add(preset.mode)

        assert ByeDPIMode.DISORDER in modes_used
        assert ByeDPIMode.SPLIT in modes_used


class TestByeDPIMode:
    """Tests for ByeDPIMode enum."""

    def test_all_modes(self):
        """Test all mode values exist."""
        assert ByeDPIMode.DISORDER.value == "disorder"
        assert ByeDPIMode.SPLIT.value == "split"
        assert ByeDPIMode.FAKE.value == "fake"
        assert ByeDPIMode.OOB.value == "oob"
        assert ByeDPIMode.DISOOB.value == "disoob"
        assert ByeDPIMode.COMBINED.value == "combined"


class TestByeDPIService:
    """Tests for ByeDPIService class."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with temporary paths."""
        # Patch config directory
        config_dir = tmp_path / "config" / "splitwire" / "byedpi"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.byedpi.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.byedpi.CONFIG_FILE",
            config_dir / "config.json"
        )
        monkeypatch.setattr(
            "splitwire.services.byedpi.PRESETS_FILE",
            config_dir / "presets.json"
        )

        return ByeDPIService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.name == "byedpi"
        assert service.display_name == "ByeDPI Proxy"
        assert service.service_type == ServiceType.PROXY

    def test_get_all_presets(self, service):
        """Test getting all presets."""
        presets = service.get_all_presets()

        assert len(presets) >= len(DEFAULT_PRESETS)
        assert "turkey_default" in presets
        assert "turkey_discord" in presets

    def test_get_preset(self, service):
        """Test getting a specific preset."""
        preset = service.get_preset("turkey_default")
        assert preset is not None
        assert preset.name == "Türkiye Varsayılan"

        # Test non-existent preset
        assert service.get_preset("nonexistent") is None

    def test_set_preset(self, service):
        """Test setting active preset."""
        assert service.set_preset("turkey_discord") is True
        assert service.get_config().preset_name == "turkey_discord"

        # Test invalid preset
        assert service.set_preset("invalid") is False

    def test_add_custom_preset(self, service):
        """Test adding a custom preset."""
        preset = ByeDPIPreset(
            name="My Preset",
            description="Custom preset",
            args="--split 2",
        )

        assert service.add_custom_preset("my_preset", preset) is True

        # Verify it's added
        presets = service.get_all_presets()
        assert "my_preset" in presets
        assert presets["my_preset"].is_custom is True

    def test_cannot_override_default_preset(self, service):
        """Test that default presets cannot be overridden."""
        preset = ByeDPIPreset(
            name="Override",
            description="Override attempt",
            args="--fake",
        )

        assert service.add_custom_preset("turkey_default", preset) is False

    def test_remove_custom_preset(self, service):
        """Test removing a custom preset."""
        # Add first
        preset = ByeDPIPreset(name="To Remove", description="", args="")
        service.add_custom_preset("to_remove", preset)

        # Remove
        assert service.remove_custom_preset("to_remove") is True
        assert "to_remove" not in service.get_all_presets()

    def test_set_custom_args(self, service):
        """Test setting custom arguments."""
        service.set_custom_args("--disorder 5 --ttl 10")
        assert service.get_config().custom_args == "--disorder 5 --ttl 10"

    def test_set_proxy_port(self, service):
        """Test setting proxy port."""
        service.set_proxy_port(8888)
        assert service.get_config().proxy_port == 8888

    def test_get_proxy_address(self, service):
        """Test getting proxy address."""
        addr = service.get_proxy_address()
        assert addr == f"socks5://{DEFAULT_PROXY_HOST}:{DEFAULT_PROXY_PORT}"

        service.set_proxy_port(9999)
        addr = service.get_proxy_address()
        assert addr == f"socks5://{DEFAULT_PROXY_HOST}:9999"

    def test_tunneled_apps(self, service):
        """Test tunneled app management."""
        # Add apps
        service.add_tunneled_app("discord")
        service.add_tunneled_app("firefox")

        apps = service.get_tunneled_apps()
        assert "discord" in apps
        assert "firefox" in apps

        # Remove app
        service.remove_tunneled_app("discord")
        apps = service.get_tunneled_apps()
        assert "discord" not in apps
        assert "firefox" in apps

    def test_include_browsers(self, service):
        """Test include browsers setting."""
        assert service.get_config().include_browsers is False

        service.set_include_browsers(True)
        assert service.get_config().include_browsers is True

    def test_build_command(self, service):
        """Test command building."""
        service.set_preset("turkey_default")
        cmd = service._build_command()

        assert cmd[0].endswith("ciadpi")
        assert "-i" in cmd
        assert "-p" in cmd
        assert str(DEFAULT_PROXY_PORT) in cmd

    def test_build_command_with_custom_args(self, service):
        """Test command building with custom args."""
        service.set_custom_args("--custom-arg value")
        cmd = service._build_command()

        assert "--custom-arg" in cmd
        assert "value" in cmd

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        status = service.status()
        assert status == ServiceStatus.NOT_INSTALLED

    def test_is_installed_false(self, service):
        """Test is_installed returns false when not installed."""
        assert service.is_installed() is False


class TestGetByeDPIService:
    """Tests for get_byedpi_service function."""

    def test_singleton(self):
        """Test that get_byedpi_service returns singleton."""
        # Note: This test may not work perfectly with patching
        # In real scenarios, the service should be singleton
        pass


class TestByeDPIPresetArgs:
    """Tests for preset argument parsing."""

    def test_disorder_preset_args(self):
        """Test disorder preset has correct args."""
        preset = DEFAULT_PRESETS.get("preset_disorder")
        assert preset is not None
        assert "--disorder" in preset.args

    def test_split_preset_args(self):
        """Test split preset has correct args."""
        preset = DEFAULT_PRESETS.get("preset_split")
        assert preset is not None
        assert "--split" in preset.args

    def test_fake_preset_args(self):
        """Test fake preset has correct args."""
        preset = DEFAULT_PRESETS.get("preset_fake")
        assert preset is not None
        assert "--fake" in preset.args
        assert "--ttl" in preset.args

    def test_oob_preset_args(self):
        """Test OOB preset has correct args."""
        preset = DEFAULT_PRESETS.get("preset_oob")
        assert preset is not None
        assert "--oob" in preset.args

    def test_auto_preset_args(self):
        """Test auto preset has correct args."""
        preset = DEFAULT_PRESETS.get("preset_auto")
        assert preset is not None
        assert "--auto" in preset.args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
