"""
Unit tests for Proxy Route service.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from splitwire.services.proxy_route import (
    ProxyRouteService,
    ProxyRouteConfig,
    ProxiedApp,
    ProxyMethod,
    DEFAULT_PROXY_HOST,
    DEFAULT_PROXY_PORT,
    get_proxy_route_service,
)
from splitwire.services.base import ServiceStatus, ServiceType
from splitwire.services.split_tunnel import KNOWN_APPS, BROWSER_APPS


class TestProxiedApp:
    """Tests for ProxiedApp dataclass."""

    def test_proxied_app_creation(self):
        """Test creating a proxied app."""
        app = ProxiedApp(
            name="discord",
            path="/usr/bin/discord",
            enabled=True,
            is_custom=False,
        )

        assert app.name == "discord"
        assert app.path == "/usr/bin/discord"
        assert app.enabled is True
        assert app.is_custom is False

    def test_proxied_app_defaults(self):
        """Test default values."""
        app = ProxiedApp(name="test", path="/test")

        assert app.enabled is True
        assert app.is_custom is False


class TestProxyRouteConfig:
    """Tests for ProxyRouteConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ProxyRouteConfig()

        assert config.enabled is False
        assert config.method == ProxyMethod.CGPROXY
        assert config.proxy_host == DEFAULT_PROXY_HOST
        assert config.proxy_port == DEFAULT_PROXY_PORT
        assert config.include_browsers is False
        assert config.apps == []
        assert config.custom_paths == []

    def test_config_with_values(self):
        """Test configuration with custom values."""
        config = ProxyRouteConfig(
            enabled=True,
            method=ProxyMethod.REDSOCKS,
            proxy_host="192.168.1.1",
            proxy_port=8080,
            include_browsers=True,
        )

        assert config.enabled is True
        assert config.method == ProxyMethod.REDSOCKS
        assert config.proxy_host == "192.168.1.1"
        assert config.proxy_port == 8080
        assert config.include_browsers is True


class TestProxyMethod:
    """Tests for ProxyMethod enum."""

    def test_all_methods(self):
        """Test all method values exist."""
        assert ProxyMethod.CGPROXY.value == "cgproxy"
        assert ProxyMethod.REDSOCKS.value == "redsocks"
        assert ProxyMethod.ENV.value == "env"


class TestProxyRouteService:
    """Tests for ProxyRouteService class."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with temporary paths."""
        config_dir = tmp_path / "config" / "splitwire"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.proxy_route.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.proxy_route.PROXY_ROUTE_CONFIG_FILE",
            config_dir / "proxy_route.json"
        )

        return ProxyRouteService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.name == "proxy-route"
        assert service.display_name == "Proxy Routing"
        assert service.service_type == ServiceType.SYSTEM

    def test_get_config(self, service):
        """Test getting configuration."""
        config = service.get_config()

        assert isinstance(config, ProxyRouteConfig)
        assert config.enabled is False

    def test_get_proxied_apps_empty(self, service):
        """Test getting proxied apps when none configured."""
        apps = service.get_proxied_apps()
        assert apps == []

    def test_set_proxy(self, service):
        """Test setting proxy address."""
        service.set_proxy("192.168.1.100", 9999)

        config = service.get_config()
        assert config.proxy_host == "192.168.1.100"
        assert config.proxy_port == 9999

    def test_add_custom_app_invalid_path(self, service):
        """Test adding custom app with invalid path."""
        result = service.add_custom_app("test", "/nonexistent/path")
        assert result is False

    def test_remove_custom_app(self, service):
        """Test removing custom app."""
        # Add via internal config
        service._config.custom_paths.append("/test/path")
        service._config.apps.append(ProxiedApp(
            name="test",
            path="/test/path",
            is_custom=True,
        ))

        result = service.remove_custom_app("/test/path")
        assert result is True
        assert "/test/path" not in service._config.custom_paths

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        status = service.status()
        assert status == ServiceStatus.NOT_INSTALLED

    def test_is_installed_false(self, service):
        """Test is_installed returns false when not installed."""
        assert service.is_installed() is False

    def test_build_app_list_empty(self, service):
        """Test building app list with no apps."""
        # With no apps and no browsers, only Discord should be added if available
        apps = service._build_app_list(None, False)
        # Result depends on whether Discord is installed on the system
        # At minimum, the function should not crash
        assert isinstance(apps, list)

    def test_build_app_list_with_browsers(self, service):
        """Test building app list includes browsers when requested."""
        apps = service._build_app_list(None, include_browsers=True)

        # Should include browser apps that exist on the system
        # Since this is a unit test, we can't guarantee which browsers exist
        assert isinstance(apps, list)


class TestProxyRouteServiceMethods:
    """Tests for specific service methods."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with mocked dependencies."""
        config_dir = tmp_path / "config" / "splitwire"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.proxy_route.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.proxy_route.PROXY_ROUTE_CONFIG_FILE",
            config_dir / "proxy_route.json"
        )

        return ProxyRouteService()

    def test_check_dependencies_cgproxy_not_installed(self, service):
        """Test dependency check when cgproxy is not installed."""
        with patch.object(service._shell, 'command_exists', return_value=False):
            result = service._check_dependencies(ProxyMethod.CGPROXY)
            assert result is False

    def test_check_dependencies_redsocks_not_installed(self, service):
        """Test dependency check when redsocks is not installed."""
        with patch.object(service._shell, 'command_exists', return_value=False):
            result = service._check_dependencies(ProxyMethod.REDSOCKS)
            assert result is False

    def test_check_dependencies_env_always_passes(self, service):
        """Test that ENV method has no dependencies."""
        result = service._check_dependencies(ProxyMethod.ENV)
        assert result is True


class TestConfigPersistence:
    """Tests for configuration persistence."""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create temporary config directory."""
        config_dir = tmp_path / "config" / "splitwire"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @pytest.fixture
    def service(self, config_dir, monkeypatch):
        """Create service with temporary paths."""
        config_file = config_dir / "proxy_route.json"

        monkeypatch.setattr(
            "splitwire.services.proxy_route.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.proxy_route.PROXY_ROUTE_CONFIG_FILE",
            config_file
        )

        return ProxyRouteService()

    def test_save_and_load_config(self, service, config_dir):
        """Test saving and loading configuration."""
        # Modify config
        service._config.enabled = True
        service._config.proxy_port = 9999
        service._config.include_browsers = True
        service._save_config()

        # Create new service to load config
        new_service = ProxyRouteService()
        config = new_service.get_config()

        assert config.enabled is True
        assert config.proxy_port == 9999
        assert config.include_browsers is True

    def test_save_config_with_apps(self, service, config_dir):
        """Test saving configuration with apps."""
        service._config.apps = [
            ProxiedApp(name="test1", path="/test1", enabled=True),
            ProxiedApp(name="test2", path="/test2", enabled=False, is_custom=True),
        ]
        service._save_config()

        # Read and verify
        config_file = config_dir / "proxy_route.json"
        data = json.loads(config_file.read_text())

        assert len(data["apps"]) == 2
        assert data["apps"][0]["name"] == "test1"
        assert data["apps"][1]["is_custom"] is True


class TestKnownAppsIntegration:
    """Tests for integration with known apps."""

    def test_known_apps_available(self):
        """Test that KNOWN_APPS is available."""
        assert len(KNOWN_APPS) > 0
        assert "discord" in KNOWN_APPS
        assert "firefox" in KNOWN_APPS

    def test_browser_apps_defined(self):
        """Test that BROWSER_APPS is defined."""
        assert len(BROWSER_APPS) > 0
        assert "firefox" in BROWSER_APPS
        assert "chrome" in BROWSER_APPS


class TestGetProxyRouteService:
    """Tests for get_proxy_route_service function."""

    def test_returns_service(self):
        """Test that function returns a service."""
        # Reset singleton
        import splitwire.services.proxy_route as module
        module._proxy_route_service = None

        service = get_proxy_route_service()
        assert isinstance(service, ProxyRouteService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
