"""
Tests for the Zapret DPI bypass service module.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.zapret import (
    ZapretService,
    ZapretConfig,
    ZapretPreset,
    ZapretMode,
    get_zapret_service,
    DEFAULT_PRESETS,
    NFQUEUE_NUM,
    TPWS_PORT,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestZapretPreset:
    """Tests for ZapretPreset dataclass."""

    def test_basic_creation(self):
        """Test creating ZapretPreset."""
        preset = ZapretPreset(
            name="Test",
            description="Test preset",
            nfqws_args="--dpi-desync=fake",
        )
        assert preset.name == "Test"
        assert preset.description == "Test preset"
        assert preset.mode == ZapretMode.NFQWS
        assert preset.is_custom is False

    def test_tpws_preset(self):
        """Test creating TPWS preset."""
        preset = ZapretPreset(
            name="TPWS Test",
            description="TPWS preset",
            tpws_args="--split-pos=3",
            mode=ZapretMode.TPWS,
        )
        assert preset.mode == ZapretMode.TPWS
        assert preset.tpws_args == "--split-pos=3"

    def test_combined_preset(self):
        """Test creating combined preset."""
        preset = ZapretPreset(
            name="Combined",
            description="Both modes",
            nfqws_args="--dpi-desync=fake",
            tpws_args="--split-pos=3",
            mode=ZapretMode.COMBINED,
        )
        assert preset.mode == ZapretMode.COMBINED
        assert preset.nfqws_args != ""
        assert preset.tpws_args != ""


class TestZapretConfig:
    """Tests for ZapretConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = ZapretConfig()
        assert config.enabled is False
        assert config.mode == ZapretMode.NFQWS
        assert config.preset_name == "turkey_discord"
        assert config.use_blacklist is False
        assert 80 in config.http_ports
        assert 443 in config.https_ports

    def test_custom_config(self):
        """Test custom configuration."""
        config = ZapretConfig(
            enabled=True,
            mode=ZapretMode.TPWS,
            preset_name="preset_tpws",
            use_blacklist=True,
            http_ports=[80, 8080],
            https_ports=[443, 8443],
        )
        assert config.enabled is True
        assert config.mode == ZapretMode.TPWS
        assert 8080 in config.http_ports


class TestDefaultPresets:
    """Tests for default presets."""

    def test_presets_structure(self):
        """Test DEFAULT_PRESETS has correct structure."""
        assert isinstance(DEFAULT_PRESETS, dict)
        assert len(DEFAULT_PRESETS) >= 5  # At least 5 presets

    def test_turkey_discord_preset(self):
        """Test Turkey Discord preset exists and has args."""
        assert "turkey_discord" in DEFAULT_PRESETS
        preset = DEFAULT_PRESETS["turkey_discord"]
        assert preset.name == "Türkiye Discord"
        assert "dpi-desync" in preset.nfqws_args
        assert preset.mode == ZapretMode.NFQWS

    def test_turkey_general_preset(self):
        """Test Turkey General preset."""
        assert "turkey_general" in DEFAULT_PRESETS
        preset = DEFAULT_PRESETS["turkey_general"]
        assert preset.mode == ZapretMode.NFQWS

    def test_tpws_preset_exists(self):
        """Test TPWS mode preset exists."""
        assert "preset_tpws" in DEFAULT_PRESETS
        preset = DEFAULT_PRESETS["preset_tpws"]
        assert preset.mode == ZapretMode.TPWS
        assert preset.tpws_args != ""


class TestZapretService:
    """Tests for ZapretService class."""

    @pytest.fixture
    def service(self):
        """Create a Zapret service instance."""
        with patch('splitwire.services.zapret.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.zapret.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                with patch('splitwire.services.zapret.LOCAL_CONFIG_DIR', Path(tempfile.mkdtemp())):
                    service = ZapretService()
                    return service

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "zapret"
        assert service.display_name == "Zapret DPI Bypass"
        assert service.service_type == ServiceType.DPI_BYPASS

    def test_not_installed_initially(self, service):
        """Test service is not installed by default."""
        with patch.object(Path, 'exists', return_value=False):
            assert not service.is_installed()

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        with patch.object(service, 'is_installed', return_value=False):
            assert service.status() == ServiceStatus.NOT_INSTALLED

    def test_get_presets(self, service):
        """Test getting presets."""
        presets = service.get_presets()
        assert "turkey_discord" in presets
        assert "turkey_general" in presets
        assert isinstance(presets["turkey_discord"], ZapretPreset)

    def test_get_preset(self, service):
        """Test getting specific preset."""
        preset = service.get_preset("turkey_discord")
        assert preset is not None
        assert preset.name == "Türkiye Discord"

        # Non-existent preset
        assert service.get_preset("nonexistent") is None

    def test_set_preset(self, service):
        """Test setting active preset."""
        assert service._config.preset_name == "turkey_discord"
        result = service.set_preset("turkey_general")
        assert result is True
        assert service._config.preset_name == "turkey_general"

        # Invalid preset
        result = service.set_preset("nonexistent")
        assert result is False

    def test_add_custom_preset(self, service):
        """Test adding custom preset."""
        custom = ZapretPreset(
            name="My Custom",
            description="Custom preset",
            nfqws_args="--dpi-desync=split",
        )
        result = service.add_custom_preset("my_custom", custom)
        assert result is True
        assert "my_custom" in service.get_presets()
        assert service.get_presets()["my_custom"].is_custom is True

    def test_remove_custom_preset(self, service):
        """Test removing custom preset."""
        # Add first
        custom = ZapretPreset(
            name="To Remove",
            description="Will be removed",
            nfqws_args="--test",
        )
        service.add_custom_preset("to_remove", custom)
        assert "to_remove" in service.get_presets()

        # Remove
        result = service.remove_custom_preset("to_remove")
        assert result is True
        assert "to_remove" not in service.get_presets()

        # Cannot remove built-in
        result = service.remove_custom_preset("turkey_discord")
        assert result is False


class TestZapretBlacklist:
    """Tests for blacklist functionality."""

    @pytest.fixture
    def service(self):
        """Create a Zapret service with temp config dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('splitwire.services.zapret.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                with patch('splitwire.services.zapret.get_shell') as mock_shell:
                    mock_shell.return_value = MagicMock()
                    with patch('splitwire.services.zapret.LOCAL_CONFIG_DIR', Path(tmpdir)):
                        with patch('splitwire.services.zapret.BLACKLIST_FILE', Path(tmpdir) / "blacklist.txt"):
                            service = ZapretService()
                            yield service

    def test_empty_blacklist(self, service):
        """Test getting empty blacklist."""
        domains = service.get_blacklist()
        assert domains == []

    def test_set_blacklist(self, service):
        """Test setting blacklist."""
        domains = ["discord.com", "discord.gg", "rutracker.org"]
        result = service.set_blacklist(domains)
        assert result is True

        retrieved = service.get_blacklist()
        assert "discord.com" in retrieved
        assert "discord.gg" in retrieved
        assert len(retrieved) == 3

    def test_add_to_blacklist(self, service):
        """Test adding to blacklist."""
        service.set_blacklist(["discord.com"])
        result = service.add_to_blacklist("twitter.com")
        assert result is True

        domains = service.get_blacklist()
        assert "discord.com" in domains
        assert "twitter.com" in domains

    def test_remove_from_blacklist(self, service):
        """Test removing from blacklist."""
        service.set_blacklist(["discord.com", "twitter.com"])
        result = service.remove_from_blacklist("twitter.com")
        assert result is True

        domains = service.get_blacklist()
        assert "discord.com" in domains
        assert "twitter.com" not in domains


class TestZapretNfqwsArgs:
    """Tests for nfqws argument building."""

    @pytest.fixture
    def service(self):
        """Create a Zapret service instance."""
        with patch('splitwire.services.zapret.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.zapret.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                with patch('splitwire.services.zapret.LOCAL_CONFIG_DIR', Path(tempfile.mkdtemp())):
                    service = ZapretService()
                    return service

    def test_build_nfqws_args_with_preset(self, service):
        """Test building nfqws args from preset."""
        preset = DEFAULT_PRESETS["turkey_discord"]
        args = service._build_nfqws_args(preset)

        assert "--qnum" in args
        assert str(NFQUEUE_NUM) in args
        assert "--dpi-desync" in " ".join(args)

    def test_build_nfqws_args_custom(self, service):
        """Test building nfqws args with custom args."""
        service._config.custom_nfqws_args = "--dpi-desync=split --test-arg"
        args = service._build_nfqws_args(None)

        assert "--dpi-desync=split" in args
        assert "--test-arg" in args


class TestZapretTpwsArgs:
    """Tests for tpws argument building."""

    @pytest.fixture
    def service(self):
        """Create a Zapret service instance."""
        with patch('splitwire.services.zapret.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.zapret.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                with patch('splitwire.services.zapret.LOCAL_CONFIG_DIR', Path(tempfile.mkdtemp())):
                    service = ZapretService()
                    return service

    def test_build_tpws_args_with_preset(self, service):
        """Test building tpws args from preset."""
        preset = DEFAULT_PRESETS["preset_tpws"]
        args = service._build_tpws_args(preset)

        assert "--port" in args
        assert str(TPWS_PORT) in args
        assert "--split-pos" in " ".join(args)

    def test_build_tpws_args_custom(self, service):
        """Test building tpws args with custom args."""
        service._config.custom_tpws_args = "--split-pos=5 --oob"
        args = service._build_tpws_args(None)

        assert "--split-pos=5" in args
        assert "--oob" in args


class TestZapretConfig:
    """Tests for configuration save/load."""

    def test_config_save_load(self):
        """Test configuration persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "custom.json"

            with patch('splitwire.services.zapret.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                with patch('splitwire.services.zapret.get_shell') as mock_shell:
                    mock_shell.return_value = MagicMock()
                    with patch('splitwire.services.zapret.LOCAL_CONFIG_DIR', Path(tmpdir)):
                        with patch('splitwire.services.zapret.CUSTOM_CONFIG_FILE', config_file):
                            # Create service and modify config
                            service = ZapretService()
                            service._config.preset_name = "turkey_general"
                            service._config.use_blacklist = True
                            service._save_config()

                            # Create new service and verify loaded
                            service2 = ZapretService()
                            assert service2._config.preset_name == "turkey_general"
                            assert service2._config.use_blacklist is True


class TestZapretServiceIntegration:
    """Integration tests for Zapret service."""

    def test_get_zapret_service_singleton(self):
        """Test that get_zapret_service returns singleton."""
        import splitwire.services.zapret as zapret_module
        zapret_module._zapret_service = None

        service1 = get_zapret_service()
        service2 = get_zapret_service()
        assert service1 is service2

    def test_zapret_mode_enum(self):
        """Test ZapretMode enum values."""
        assert ZapretMode.NFQWS.value == "nfqws"
        assert ZapretMode.TPWS.value == "tpws"
        assert ZapretMode.COMBINED.value == "combined"


class TestConstants:
    """Tests for module constants."""

    def test_nfqueue_num(self):
        """Test NFQUEUE number is valid."""
        assert isinstance(NFQUEUE_NUM, int)
        assert NFQUEUE_NUM > 0
        assert NFQUEUE_NUM < 65536

    def test_tpws_port(self):
        """Test TPWS port is valid."""
        assert isinstance(TPWS_PORT, int)
        assert TPWS_PORT > 0
        assert TPWS_PORT < 65536
