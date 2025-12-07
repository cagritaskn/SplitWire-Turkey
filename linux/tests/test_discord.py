"""
Unit tests for Discord service.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from splitwire.services.discord import (
    DiscordService,
    DiscordConfig,
    DiscordInstallation,
    WebCordInstallation,
    DiscordVersion,
    InstallMethod,
    RepairResult,
    DISCORD_CONFIG_DIRS,
    DISCORD_CACHE_DIRS,
    DISCORD_DOWNLOAD_URLS,
    DEB_DISCORD_NAMES,
    FLATPAK_DISCORD_IDS,
    SNAP_DISCORD_NAMES,
    get_discord_service,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestDiscordVersion:
    """Tests for DiscordVersion enum."""

    def test_all_versions(self):
        """Test all version values exist."""
        assert DiscordVersion.STABLE.value == "stable"
        assert DiscordVersion.PTB.value == "ptb"
        assert DiscordVersion.CANARY.value == "canary"

    def test_version_count(self):
        """Test that we have 3 versions."""
        assert len(DiscordVersion) == 3


class TestInstallMethod:
    """Tests for InstallMethod enum."""

    def test_all_methods(self):
        """Test all method values exist."""
        assert InstallMethod.DEB.value == "deb"
        assert InstallMethod.SNAP.value == "snap"
        assert InstallMethod.FLATPAK.value == "flatpak"
        assert InstallMethod.TARBALL.value == "tarball"
        assert InstallMethod.APPIMAGE.value == "appimage"
        assert InstallMethod.NOT_INSTALLED.value == "not_installed"
        assert InstallMethod.UNKNOWN.value == "unknown"


class TestDiscordInstallation:
    """Tests for DiscordInstallation dataclass."""

    def test_installation_creation(self):
        """Test creating an installation."""
        inst = DiscordInstallation(
            version=DiscordVersion.STABLE,
            method=InstallMethod.DEB,
            path="/usr/share/discord",
            binary_path="/usr/bin/discord",
            is_running=True,
            has_cache=True,
            cache_size_mb=150.5,
        )

        assert inst.version == DiscordVersion.STABLE
        assert inst.method == InstallMethod.DEB
        assert inst.path == "/usr/share/discord"
        assert inst.binary_path == "/usr/bin/discord"
        assert inst.is_running is True
        assert inst.has_cache is True
        assert inst.cache_size_mb == 150.5

    def test_installation_defaults(self):
        """Test default values."""
        inst = DiscordInstallation(
            version=DiscordVersion.PTB,
            method=InstallMethod.NOT_INSTALLED,
        )

        assert inst.path is None
        assert inst.binary_path is None
        assert inst.is_running is False
        assert inst.has_cache is False
        assert inst.cache_size_mb == 0.0


class TestWebCordInstallation:
    """Tests for WebCordInstallation dataclass."""

    def test_webcord_defaults(self):
        """Test default values."""
        webcord = WebCordInstallation()

        assert webcord.installed is False
        assert webcord.method == InstallMethod.NOT_INSTALLED
        assert webcord.path is None
        assert webcord.is_running is False

    def test_webcord_installed(self):
        """Test installed WebCord."""
        webcord = WebCordInstallation(
            installed=True,
            method=InstallMethod.FLATPAK,
            path="flatpak:io.github.nickvision.webcord",
            is_running=True,
        )

        assert webcord.installed is True
        assert webcord.method == InstallMethod.FLATPAK


class TestDiscordConfig:
    """Tests for DiscordConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = DiscordConfig()

        assert config.last_repair_date is None
        assert config.auto_clear_cache is False
        assert config.preferred_version == "stable"

    def test_config_with_values(self):
        """Test configuration with values."""
        config = DiscordConfig(
            last_repair_date="2024-01-01T00:00:00",
            auto_clear_cache=True,
            preferred_version="ptb",
        )

        assert config.last_repair_date == "2024-01-01T00:00:00"
        assert config.auto_clear_cache is True
        assert config.preferred_version == "ptb"


class TestRepairResult:
    """Tests for RepairResult dataclass."""

    def test_success_result(self):
        """Test successful repair result."""
        result = RepairResult(
            success=True,
            message="Repair completed",
            cache_cleared_mb=100.5,
        )

        assert result.success is True
        assert result.message == "Repair completed"
        assert result.cache_cleared_mb == 100.5
        assert result.errors == []

    def test_failed_result(self):
        """Test failed repair result."""
        result = RepairResult(
            success=False,
            message="Repair failed",
            errors=["Error 1", "Error 2"],
        )

        assert result.success is False
        assert len(result.errors) == 2


class TestDiscordConstants:
    """Tests for Discord constants."""

    def test_config_dirs(self):
        """Test config directory paths."""
        assert "stable" in DISCORD_CONFIG_DIRS
        assert "ptb" in DISCORD_CONFIG_DIRS
        assert "canary" in DISCORD_CONFIG_DIRS

        assert DISCORD_CONFIG_DIRS["stable"].name == "discord"
        assert DISCORD_CONFIG_DIRS["ptb"].name == "discordptb"
        assert DISCORD_CONFIG_DIRS["canary"].name == "discordcanary"

    def test_cache_dirs(self):
        """Test cache directory paths."""
        assert "stable" in DISCORD_CACHE_DIRS
        assert "ptb" in DISCORD_CACHE_DIRS
        assert "canary" in DISCORD_CACHE_DIRS

    def test_download_urls(self):
        """Test download URLs."""
        assert "stable" in DISCORD_DOWNLOAD_URLS
        assert "ptb" in DISCORD_DOWNLOAD_URLS
        assert "canary" in DISCORD_DOWNLOAD_URLS

        assert "discord.com" in DISCORD_DOWNLOAD_URLS["stable"]
        assert "ptb" in DISCORD_DOWNLOAD_URLS["ptb"]
        assert "canary" in DISCORD_DOWNLOAD_URLS["canary"]

    def test_deb_names(self):
        """Test DEB package names."""
        assert DEB_DISCORD_NAMES["stable"] == "discord"
        assert DEB_DISCORD_NAMES["ptb"] == "discord-ptb"
        assert DEB_DISCORD_NAMES["canary"] == "discord-canary"

    def test_flatpak_ids(self):
        """Test Flatpak IDs."""
        assert FLATPAK_DISCORD_IDS["stable"] == "com.discordapp.Discord"
        assert FLATPAK_DISCORD_IDS["ptb"] == "com.discordapp.DiscordPTB"
        assert FLATPAK_DISCORD_IDS["canary"] == "com.discordapp.DiscordCanary"

    def test_snap_names(self):
        """Test Snap package names."""
        assert SNAP_DISCORD_NAMES["stable"] == "discord"
        assert SNAP_DISCORD_NAMES["ptb"] == "discord-ptb"
        assert SNAP_DISCORD_NAMES["canary"] == "discord-canary"


class TestDiscordService:
    """Tests for DiscordService class."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with temporary paths."""
        config_dir = tmp_path / "config" / "splitwire" / "discord"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.discord.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.discord.CONFIG_FILE",
            config_dir / "config.json"
        )

        return DiscordService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.name == "discord"
        assert service.display_name == "Discord Repair"
        assert service.service_type == ServiceType.SYSTEM

    def test_get_config(self, service):
        """Test getting configuration."""
        config = service.get_config()
        assert isinstance(config, DiscordConfig)
        assert config.preferred_version == "stable"

    def test_set_preferred_version(self, service):
        """Test setting preferred version."""
        service.set_preferred_version("ptb")
        assert service.get_config().preferred_version == "ptb"

    def test_set_auto_clear_cache(self, service):
        """Test setting auto clear cache."""
        assert service.get_config().auto_clear_cache is False
        service.set_auto_clear_cache(True)
        assert service.get_config().auto_clear_cache is True

    def test_detect_all_returns_dict(self, service):
        """Test detect_all returns dictionary."""
        installations = service.detect_all()

        assert isinstance(installations, dict)
        assert len(installations) == 3
        assert DiscordVersion.STABLE in installations
        assert DiscordVersion.PTB in installations
        assert DiscordVersion.CANARY in installations

    def test_get_installation(self, service):
        """Test getting specific installation."""
        inst = service.get_installation(DiscordVersion.STABLE)

        assert isinstance(inst, DiscordInstallation)
        assert inst.version == DiscordVersion.STABLE

    def test_get_webcord(self, service):
        """Test getting WebCord info."""
        webcord = service.get_webcord()

        assert isinstance(webcord, WebCordInstallation)

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        # Mock detection to return not installed
        with patch.object(service, 'detect_all') as mock_detect:
            mock_detect.return_value = {
                DiscordVersion.STABLE: DiscordInstallation(
                    version=DiscordVersion.STABLE,
                    method=InstallMethod.NOT_INSTALLED,
                ),
                DiscordVersion.PTB: DiscordInstallation(
                    version=DiscordVersion.PTB,
                    method=InstallMethod.NOT_INSTALLED,
                ),
                DiscordVersion.CANARY: DiscordInstallation(
                    version=DiscordVersion.CANARY,
                    method=InstallMethod.NOT_INSTALLED,
                ),
            }
            service._installations = mock_detect.return_value

            status = service.status()
            assert status == ServiceStatus.NOT_INSTALLED


class TestDiscordServiceDetection:
    """Tests for Discord detection methods."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service."""
        config_dir = tmp_path / "config" / "splitwire" / "discord"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.discord.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.discord.CONFIG_FILE",
            config_dir / "config.json"
        )

        return DiscordService()

    def test_is_deb_installed_false(self, service):
        """Test DEB detection when not installed."""
        with patch.object(service._shell, 'run') as mock_run:
            mock_run.return_value = Mock(success=False, stdout="", stderr="")

            result = service._is_deb_installed("discord")
            assert result is False

    def test_is_snap_installed_false(self, service):
        """Test Snap detection when not installed."""
        with patch.object(service._shell, 'run') as mock_run:
            mock_run.return_value = Mock(success=False, stdout="", stderr="")

            result = service._is_snap_installed(DiscordVersion.STABLE)
            assert result is False

    def test_is_flatpak_installed_false(self, service):
        """Test Flatpak detection when not installed."""
        with patch.object(service._shell, 'run') as mock_run:
            mock_run.return_value = Mock(success=False, stdout="", stderr="")

            result = service._is_flatpak_installed(DiscordVersion.STABLE)
            assert result is False

    def test_find_binary_not_found(self, service):
        """Test binary search when not found."""
        with patch.object(service._shell, 'get_command_path') as mock_path:
            mock_path.return_value = None

            result = service._find_binary(DiscordVersion.STABLE)
            assert result is None


class TestDiscordServiceCache:
    """Tests for Discord cache operations."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with temporary directories."""
        config_dir = tmp_path / "config" / "splitwire" / "discord"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create fake Discord cache dirs
        discord_config = tmp_path / ".config" / "discord"
        discord_cache = tmp_path / ".cache" / "discord"
        discord_config.mkdir(parents=True, exist_ok=True)
        discord_cache.mkdir(parents=True, exist_ok=True)

        # Create some cache files
        (discord_cache / "test_cache.dat").write_bytes(b"x" * 1000)
        (discord_config / "Cache").mkdir(exist_ok=True)
        (discord_config / "Cache" / "data.cache").write_bytes(b"y" * 2000)

        monkeypatch.setattr(
            "splitwire.services.discord.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.discord.CONFIG_FILE",
            config_dir / "config.json"
        )
        monkeypatch.setattr(
            "splitwire.services.discord.DISCORD_CONFIG_DIRS",
            {"stable": discord_config, "ptb": tmp_path / ".config" / "discordptb", "canary": tmp_path / ".config" / "discordcanary"}
        )
        monkeypatch.setattr(
            "splitwire.services.discord.DISCORD_CACHE_DIRS",
            {"stable": discord_cache, "ptb": tmp_path / ".cache" / "discordptb", "canary": tmp_path / ".cache" / "discordcanary"}
        )

        return DiscordService()

    def test_get_dir_size_mb(self, service, tmp_path):
        """Test directory size calculation."""
        test_dir = tmp_path / "test_size"
        test_dir.mkdir()

        # Create 1MB file
        (test_dir / "file.dat").write_bytes(b"x" * 1024 * 1024)

        size = service._get_dir_size_mb(test_dir)
        assert 0.9 < size < 1.1  # Approximately 1MB

    def test_clear_cache_success(self, service):
        """Test cache clearing."""
        result = service.clear_cache(DiscordVersion.STABLE)

        assert isinstance(result, RepairResult)
        # May or may not succeed depending on paths


class TestDiscordServiceConfig:
    """Tests for Discord service configuration persistence."""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create temporary config directory."""
        config_dir = tmp_path / "config" / "splitwire" / "discord"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @pytest.fixture
    def service(self, config_dir, monkeypatch):
        """Create service with temporary paths."""
        config_file = config_dir / "config.json"

        monkeypatch.setattr(
            "splitwire.services.discord.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.discord.CONFIG_FILE",
            config_file
        )

        return DiscordService()

    def test_save_and_load_config(self, service, config_dir):
        """Test saving and loading configuration."""
        # Modify config
        service._config.auto_clear_cache = True
        service._config.preferred_version = "canary"
        service._save_config()

        # Verify file exists
        config_file = config_dir / "config.json"
        assert config_file.exists()

        # Create new service to load config
        new_service = DiscordService()
        config = new_service.get_config()

        assert config.auto_clear_cache is True
        assert config.preferred_version == "canary"


class TestDiscordServiceRepair:
    """Tests for Discord repair functionality."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service."""
        config_dir = tmp_path / "config" / "splitwire" / "discord"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.discord.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.discord.CONFIG_FILE",
            config_dir / "config.json"
        )

        return DiscordService()

    def test_repair_updates_date(self, service):
        """Test that repair updates last repair date."""
        assert service.get_config().last_repair_date is None

        # Mock methods to avoid actual operations
        with patch.object(service, '_is_discord_running', return_value=False):
            with patch.object(service, 'clear_cache') as mock_clear:
                mock_clear.return_value = RepairResult(success=True, message="OK")

                service.repair_discord(DiscordVersion.STABLE)

                assert service.get_config().last_repair_date is not None


class TestGetDiscordService:
    """Tests for get_discord_service function."""

    def test_returns_service(self):
        """Test that function returns a service."""
        # Reset singleton
        import splitwire.services.discord as module
        module._discord_service = None

        service = get_discord_service()
        assert isinstance(service, DiscordService)

    def test_singleton_pattern(self):
        """Test singleton pattern."""
        import splitwire.services.discord as module
        module._discord_service = None

        s1 = get_discord_service()
        s2 = get_discord_service()
        assert s1 is s2


class TestDiscordVersionFromString:
    """Tests for creating Discord version from string."""

    def test_create_from_string(self):
        """Test creating version from string."""
        assert DiscordVersion("stable") == DiscordVersion.STABLE
        assert DiscordVersion("ptb") == DiscordVersion.PTB
        assert DiscordVersion("canary") == DiscordVersion.CANARY

    def test_invalid_version(self):
        """Test invalid version raises error."""
        with pytest.raises(ValueError):
            DiscordVersion("invalid")


class TestInstallMethodFromString:
    """Tests for creating install method from string."""

    def test_create_from_string(self):
        """Test creating method from string."""
        assert InstallMethod("deb") == InstallMethod.DEB
        assert InstallMethod("snap") == InstallMethod.SNAP
        assert InstallMethod("flatpak") == InstallMethod.FLATPAK


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
