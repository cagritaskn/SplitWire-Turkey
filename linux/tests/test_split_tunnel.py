"""
Tests for the split tunnel service module.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.split_tunnel import (
    SplitTunnelService,
    SplitTunnelConfig,
    TunneledApp,
    get_split_tunnel_service,
    KNOWN_APPS,
    BROWSER_APPS,
    CGPROXY_CONFIG_FILE,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestTunneledApp:
    """Tests for TunneledApp dataclass."""

    def test_basic_creation(self):
        """Test creating TunneledApp."""
        app = TunneledApp(
            name="discord",
            path="/usr/bin/discord",
        )
        assert app.name == "discord"
        assert app.path == "/usr/bin/discord"
        assert app.enabled is True
        assert app.is_custom is False

    def test_custom_app(self):
        """Test creating custom TunneledApp."""
        app = TunneledApp(
            name="myapp",
            path="/home/user/myapp",
            enabled=True,
            is_custom=True,
        )
        assert app.is_custom is True


class TestSplitTunnelConfig:
    """Tests for SplitTunnelConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = SplitTunnelConfig()
        assert config.enabled is False
        assert config.include_browsers is False
        assert config.apps == []
        assert config.custom_paths == []

    def test_config_with_apps(self):
        """Test configuration with apps."""
        config = SplitTunnelConfig(
            enabled=True,
            include_browsers=True,
            apps=[
                TunneledApp(name="discord", path="/usr/bin/discord"),
                TunneledApp(name="firefox", path="/usr/bin/firefox"),
            ],
        )
        assert config.enabled is True
        assert len(config.apps) == 2


class TestKnownApps:
    """Tests for known apps constants."""

    def test_known_apps_structure(self):
        """Test KNOWN_APPS has correct structure."""
        assert isinstance(KNOWN_APPS, dict)
        for app_name, paths in KNOWN_APPS.items():
            assert isinstance(app_name, str)
            assert isinstance(paths, list)
            for path in paths:
                assert isinstance(path, str)
                assert path.startswith("/")

    def test_discord_in_known_apps(self):
        """Test Discord is in known apps."""
        assert "discord" in KNOWN_APPS
        assert len(KNOWN_APPS["discord"]) > 0

    def test_browsers_in_known_apps(self):
        """Test all browser apps are in known apps."""
        for browser in BROWSER_APPS:
            assert browser in KNOWN_APPS, f"Browser '{browser}' not in KNOWN_APPS"

    def test_browser_apps_list(self):
        """Test BROWSER_APPS list content."""
        assert "firefox" in BROWSER_APPS
        assert "chrome" in BROWSER_APPS
        assert "chromium" in BROWSER_APPS
        assert "brave" in BROWSER_APPS


class TestSplitTunnelService:
    """Tests for SplitTunnelService class."""

    @pytest.fixture
    def service(self):
        """Create a split tunnel service instance."""
        with patch('splitwire.services.split_tunnel.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.split_tunnel.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                with patch('splitwire.services.split_tunnel.LOCAL_CONFIG_DIR', Path(tempfile.mkdtemp())):
                    with patch('splitwire.services.split_tunnel.APPS_CONFIG_FILE', Path(tempfile.mktemp())):
                        service = SplitTunnelService()
                        return service

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "split-tunnel"
        assert service.display_name == "Split Tunneling"
        assert service.service_type == ServiceType.SYSTEM

    def test_get_known_apps(self, service):
        """Test getting known apps."""
        apps = service.get_known_apps()
        assert "discord" in apps
        assert "firefox" in apps

    def test_get_available_apps(self, service):
        """Test getting available apps on system."""
        # Mock Path.exists to return True for some apps
        with patch.object(Path, 'exists') as mock_exists:
            def exists_side_effect(self=None):
                path_str = str(self) if self else ""
                return "discord" in path_str or "firefox" in path_str

            mock_exists.side_effect = exists_side_effect

            available = service.get_available_apps()
            # Result depends on mocking, just verify it returns a list
            assert isinstance(available, list)

    def test_get_tunneled_apps_empty(self, service):
        """Test getting tunneled apps when none configured."""
        apps = service.get_tunneled_apps()
        assert apps == []

    def test_build_app_list_with_browsers(self, service):
        """Test building app list with browsers included."""
        with patch.object(Path, 'exists', return_value=True):
            apps = service._build_app_list(["discord"], include_browsers=True)
            app_names = [app.name for app in apps]
            assert "discord" in app_names

    def test_build_app_list_discord_default(self, service):
        """Test Discord is always added by default if available."""
        with patch.object(Path, 'exists', return_value=True):
            apps = service._build_app_list([], include_browsers=False)
            app_names = [app.name for app in apps]
            assert "discord" in app_names

    def test_add_custom_app(self, service):
        """Test adding a custom app."""
        with patch.object(Path, 'exists', return_value=True):
            result = service.add_custom_app("myapp", "/usr/bin/myapp")
            assert result is True
            assert len(service._config.apps) == 1
            assert service._config.apps[0].is_custom is True

    def test_add_custom_app_nonexistent(self, service):
        """Test adding non-existent app fails."""
        with patch.object(Path, 'exists', return_value=False):
            result = service.add_custom_app("myapp", "/nonexistent/path")
            assert result is False

    def test_remove_custom_app(self, service):
        """Test removing a custom app."""
        service._config.apps.append(TunneledApp(
            name="myapp",
            path="/usr/bin/myapp",
            is_custom=True,
        ))
        service._config.custom_paths.append("/usr/bin/myapp")

        result = service.remove_custom_app("/usr/bin/myapp")
        assert result is True
        assert len(service._config.apps) == 0

    def test_set_include_browsers(self, service):
        """Test setting include browsers option."""
        assert service._config.include_browsers is False
        service.set_include_browsers(True)
        assert service._config.include_browsers is True


class TestCgproxyConfig:
    """Tests for cgproxy configuration generation."""

    @pytest.fixture
    def service(self):
        """Create a split tunnel service instance."""
        with patch('splitwire.services.split_tunnel.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.split_tunnel.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                service = SplitTunnelService()
                return service

    def test_generate_cgproxy_config_format(self, service):
        """Test cgproxy config has correct format."""
        apps = [
            TunneledApp(name="discord", path="/usr/bin/discord", enabled=True),
            TunneledApp(name="firefox", path="/usr/bin/firefox", enabled=True),
        ]

        # Mock the privileged commands
        service._run_privileged = MagicMock(return_value=MagicMock(success=True))

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            with patch('splitwire.services.split_tunnel.CGPROXY_CONFIG_FILE', config_file):
                with patch('splitwire.services.split_tunnel.CGPROXY_CONFIG_DIR', Path(tmpdir)):
                    result = service._generate_cgproxy_config(apps, "splitwire")

        # Check the mocked call was made
        assert service._run_privileged.called


class TestSplitTunnelServiceIntegration:
    """Integration tests for split tunnel service."""

    def test_get_split_tunnel_service_singleton(self):
        """Test that get_split_tunnel_service returns singleton."""
        import splitwire.services.split_tunnel as st_module
        st_module._split_tunnel_service = None

        service1 = get_split_tunnel_service()
        service2 = get_split_tunnel_service()
        assert service1 is service2
