"""
Tests for the base service module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.base import (
    BaseService,
    SystemdService,
    ServiceStatus,
    ServiceType,
    ServiceInfo,
)


class TestServiceStatus:
    """Tests for ServiceStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPED.value == "stopped"
        assert ServiceStatus.FAILED.value == "failed"
        assert ServiceStatus.NOT_INSTALLED.value == "not_installed"
        assert ServiceStatus.INSTALLING.value == "installing"
        assert ServiceStatus.REMOVING.value == "removing"
        assert ServiceStatus.UNKNOWN.value == "unknown"

    def test_status_count(self):
        """Test all expected statuses are defined."""
        assert len(ServiceStatus) == 7


class TestServiceType:
    """Tests for ServiceType enum."""

    def test_type_values(self):
        """Test all type values exist."""
        assert ServiceType.VPN.value == "vpn"
        assert ServiceType.DPI_BYPASS.value == "dpi_bypass"
        assert ServiceType.PROXY.value == "proxy"
        assert ServiceType.DNS.value == "dns"
        assert ServiceType.SYSTEM.value == "system"

    def test_type_count(self):
        """Test all expected types are defined."""
        assert len(ServiceType) == 5


class TestServiceInfo:
    """Tests for ServiceInfo dataclass."""

    def test_basic_creation(self):
        """Test creating ServiceInfo with basic fields."""
        info = ServiceInfo(
            name="test",
            display_name="Test Service",
            description="A test service",
            service_type=ServiceType.SYSTEM,
        )
        assert info.name == "test"
        assert info.display_name == "Test Service"
        assert info.status == ServiceStatus.NOT_INSTALLED

    def test_full_creation(self):
        """Test creating ServiceInfo with all fields."""
        info = ServiceInfo(
            name="wireguard",
            display_name="WireGuard VPN",
            description="VPN service",
            service_type=ServiceType.VPN,
            status=ServiceStatus.RUNNING,
            version="1.0.0",
            config_path=Path("/etc/wireguard/wg0.conf"),
            systemd_unit="wg-quick@wg0.service",
            pid=1234,
            uptime=3600.0,
            metadata={"endpoint": "1.2.3.4:51820"},
        )
        assert info.status == ServiceStatus.RUNNING
        assert info.version == "1.0.0"
        assert info.pid == 1234
        assert "endpoint" in info.metadata


class TestConcreteService:
    """Tests using a concrete service implementation."""

    class MockService(BaseService):
        """Concrete implementation for testing."""

        def __init__(self):
            super().__init__(
                name="mock",
                display_name="Mock Service",
                description="A mock service for testing",
                service_type=ServiceType.SYSTEM,
            )
            self._installed = False
            self._running = False

        def install(self, **kwargs) -> bool:
            self._installed = True
            return True

        def remove(self) -> bool:
            self._installed = False
            self._running = False
            return True

        def start(self) -> bool:
            if self._installed:
                self._running = True
                return True
            return False

        def stop(self) -> bool:
            self._running = False
            return True

        def status(self) -> ServiceStatus:
            if not self._installed:
                return ServiceStatus.NOT_INSTALLED
            if self._running:
                return ServiceStatus.RUNNING
            return ServiceStatus.STOPPED

        def is_installed(self) -> bool:
            return self._installed

    @pytest.fixture
    def service(self):
        """Create a mock service instance."""
        return self.MockService()

    def test_service_properties(self, service):
        """Test service property accessors."""
        assert service.name == "mock"
        assert service.display_name == "Mock Service"
        assert service.service_type == ServiceType.SYSTEM

    def test_initial_status(self, service):
        """Test initial service status."""
        assert service.status() == ServiceStatus.NOT_INSTALLED
        assert not service.is_installed()
        assert not service.is_running()

    def test_install_and_start(self, service):
        """Test installing and starting service."""
        assert service.install()
        assert service.is_installed()
        assert service.status() == ServiceStatus.STOPPED

        assert service.start()
        assert service.is_running()
        assert service.status() == ServiceStatus.RUNNING

    def test_stop_and_remove(self, service):
        """Test stopping and removing service."""
        service.install()
        service.start()

        assert service.stop()
        assert not service.is_running()
        assert service.status() == ServiceStatus.STOPPED

        assert service.remove()
        assert not service.is_installed()
        assert service.status() == ServiceStatus.NOT_INSTALLED

    def test_restart(self, service):
        """Test restart functionality."""
        service.install()
        service.start()
        assert service.is_running()

        assert service.restart()
        assert service.is_running()

    def test_get_info(self, service):
        """Test getting service info."""
        info = service.get_info()
        assert info.name == "mock"
        assert info.display_name == "Mock Service"
        assert info.service_type == ServiceType.SYSTEM

    def test_status_callbacks(self, service):
        """Test status change callbacks."""
        callback_statuses = []

        def callback(status):
            callback_statuses.append(status)

        service.add_status_callback(callback)
        service._notify_status_change(ServiceStatus.RUNNING)

        assert ServiceStatus.RUNNING in callback_statuses

        service.remove_status_callback(callback)
        service._notify_status_change(ServiceStatus.STOPPED)

        assert ServiceStatus.STOPPED not in callback_statuses


class TestSystemdService:
    """Tests for SystemdService class."""

    class MockSystemdService(SystemdService):
        """Mock systemd service for testing."""

        def __init__(self):
            super().__init__(
                name="test",
                display_name="Test Systemd Service",
                description="Testing",
                service_type=ServiceType.SYSTEM,
                systemd_unit="test.service",
            )

        def install(self, **kwargs) -> bool:
            return True

        def remove(self) -> bool:
            return True

    @pytest.fixture
    def service(self):
        """Create a mock systemd service."""
        return self.MockSystemdService()

    def test_systemd_unit_name(self, service):
        """Test getting systemd unit name."""
        assert service._get_systemd_unit() == "test.service"

    def test_default_unit_name(self):
        """Test default systemd unit name generation."""

        class DefaultUnitService(SystemdService):
            def __init__(self):
                super().__init__(
                    name="myservice",
                    display_name="My Service",
                    description="Test",
                    service_type=ServiceType.SYSTEM,
                )

            def install(self, **kwargs) -> bool:
                return True

            def remove(self) -> bool:
                return True

        service = DefaultUnitService()
        assert service._get_systemd_unit() == "splitwire-myservice.service"
