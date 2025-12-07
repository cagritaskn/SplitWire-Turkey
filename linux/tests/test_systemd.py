"""
Tests for the systemd service manager module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from dataclasses import asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.systemd import (
    SystemdManager,
    SystemdUnitType,
    SystemdActiveState,
    SystemdEnabledState,
    SystemdUnitStatus,
    JournalEntry,
    get_systemd_manager,
)


class TestSystemdUnitType:
    """Tests for SystemdUnitType enum."""

    def test_type_values(self):
        """Test all type values exist."""
        assert SystemdUnitType.SERVICE.value == "service"
        assert SystemdUnitType.TIMER.value == "timer"
        assert SystemdUnitType.SOCKET.value == "socket"
        assert SystemdUnitType.PATH.value == "path"

    def test_type_count(self):
        """Test all expected types are defined."""
        assert len(SystemdUnitType) == 4


class TestSystemdActiveState:
    """Tests for SystemdActiveState enum."""

    def test_active_state_values(self):
        """Test all active state values exist."""
        assert SystemdActiveState.ACTIVE.value == "active"
        assert SystemdActiveState.INACTIVE.value == "inactive"
        assert SystemdActiveState.FAILED.value == "failed"
        assert SystemdActiveState.ACTIVATING.value == "activating"
        assert SystemdActiveState.DEACTIVATING.value == "deactivating"
        assert SystemdActiveState.RELOADING.value == "reloading"
        assert SystemdActiveState.UNKNOWN.value == "unknown"

    def test_active_state_count(self):
        """Test all expected states are defined."""
        assert len(SystemdActiveState) == 7


class TestSystemdEnabledState:
    """Tests for SystemdEnabledState enum."""

    def test_enabled_state_values(self):
        """Test all enabled state values exist."""
        assert SystemdEnabledState.ENABLED.value == "enabled"
        assert SystemdEnabledState.DISABLED.value == "disabled"
        assert SystemdEnabledState.STATIC.value == "static"
        assert SystemdEnabledState.MASKED.value == "masked"
        assert SystemdEnabledState.INDIRECT.value == "indirect"
        assert SystemdEnabledState.UNKNOWN.value == "unknown"

    def test_enabled_state_count(self):
        """Test all expected states are defined."""
        assert len(SystemdEnabledState) == 6


class TestSystemdUnitStatus:
    """Tests for SystemdUnitStatus dataclass."""

    def test_basic_creation(self):
        """Test creating status with required fields."""
        status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.INACTIVE,
            enabled_state=SystemdEnabledState.DISABLED,
        )
        assert status.name == "test.service"
        assert status.unit_type == SystemdUnitType.SERVICE
        assert status.active_state == SystemdActiveState.INACTIVE
        assert status.enabled_state == SystemdEnabledState.DISABLED
        assert status.description == ""
        assert status.load_state == "not-found"

    def test_full_creation(self):
        """Test creating status with all fields."""
        status = SystemdUnitStatus(
            name="splitwire-wg.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.ACTIVE,
            enabled_state=SystemdEnabledState.ENABLED,
            description="SplitWire WireGuard VPN",
            load_state="loaded",
            sub_state="running",
            main_pid=1234,
            memory_current=10485760,  # 10MB
            tasks_current=5,
            cpu_usage_nsec=1000000000,  # 1 second
            invocation_id="abc123",
            active_enter_timestamp="Mon 2024-01-01 12:00:00 UTC",
        )
        assert status.main_pid == 1234
        assert status.memory_current == 10485760
        assert status.tasks_current == 5

    def test_is_running_property(self):
        """Test is_running property."""
        active_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.ACTIVE,
            enabled_state=SystemdEnabledState.ENABLED,
        )
        assert active_status.is_running is True

        inactive_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.INACTIVE,
            enabled_state=SystemdEnabledState.ENABLED,
        )
        assert inactive_status.is_running is False

    def test_is_enabled_property(self):
        """Test is_enabled property."""
        enabled_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.ACTIVE,
            enabled_state=SystemdEnabledState.ENABLED,
        )
        assert enabled_status.is_enabled is True

        disabled_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.ACTIVE,
            enabled_state=SystemdEnabledState.DISABLED,
        )
        assert disabled_status.is_enabled is False

    def test_is_failed_property(self):
        """Test is_failed property."""
        failed_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.FAILED,
            enabled_state=SystemdEnabledState.ENABLED,
        )
        assert failed_status.is_failed is True

        active_status = SystemdUnitStatus(
            name="test.service",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.ACTIVE,
            enabled_state=SystemdEnabledState.ENABLED,
        )
        assert active_status.is_failed is False


class TestJournalEntry:
    """Tests for JournalEntry dataclass."""

    def test_basic_creation(self):
        """Test creating journal entry with required fields."""
        entry = JournalEntry(
            timestamp="1704067200000000",
            unit="test.service",
            priority=6,
            message="Service started",
        )
        assert entry.timestamp == "1704067200000000"
        assert entry.unit == "test.service"
        assert entry.priority == 6
        assert entry.message == "Service started"
        assert entry.pid is None
        assert entry.hostname is None

    def test_full_creation(self):
        """Test creating journal entry with all fields."""
        entry = JournalEntry(
            timestamp="1704067200000000",
            unit="test.service",
            priority=4,
            message="Warning: connection timeout",
            pid=1234,
            hostname="myhost",
        )
        assert entry.pid == 1234
        assert entry.hostname == "myhost"
        assert entry.priority == 4


class TestSystemdManager:
    """Tests for SystemdManager class."""

    @pytest.fixture
    def manager(self):
        """Create a SystemdManager with mocked dependencies."""
        with patch('splitwire.services.systemd.get_logger') as mock_logger, \
             patch('splitwire.services.systemd.get_shell') as mock_shell:
            mock_logger.return_value = MagicMock()
            mock_shell.return_value = MagicMock()
            mgr = SystemdManager()
            mgr._shell = mock_shell.return_value
            mgr._logger = mock_logger.return_value
            return mgr

    def test_splitwire_services_defined(self, manager):
        """Test that all SplitWire services are defined."""
        assert "wireguard" in manager.SPLITWIRE_SERVICES
        assert "wireguard-refresh" in manager.SPLITWIRE_SERVICES
        assert "zapret" in manager.SPLITWIRE_SERVICES
        assert "byedpi" in manager.SPLITWIRE_SERVICES
        assert "cgproxy" in manager.SPLITWIRE_SERVICES

    def test_splitwire_service_names(self, manager):
        """Test SplitWire service unit names."""
        assert manager.SPLITWIRE_SERVICES["wireguard"] == "splitwire-wg.service"
        assert manager.SPLITWIRE_SERVICES["wireguard-refresh"] == "splitwire-wg-refresh.timer"
        assert manager.SPLITWIRE_SERVICES["zapret"] == "splitwire-zapret.service"
        assert manager.SPLITWIRE_SERVICES["byedpi"] == "splitwire-byedpi.service"
        assert manager.SPLITWIRE_SERVICES["cgproxy"] == "splitwire-cgproxy.service"

    def test_daemon_reload(self, manager):
        """Test daemon reload."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.daemon_reload()

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "daemon-reload"],
            timeout=30
        )

    def test_daemon_reload_failure(self, manager):
        """Test daemon reload failure."""
        manager._shell.run.return_value = MagicMock(success=False, stderr="Permission denied")

        result = manager.daemon_reload()

        assert result is False

    def test_start_service(self, manager):
        """Test starting a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.start("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "start", "test.service"],
            timeout=60
        )

    def test_stop_service(self, manager):
        """Test stopping a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.stop("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "stop", "test.service"],
            timeout=60
        )

    def test_restart_service(self, manager):
        """Test restarting a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.restart("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "restart", "test.service"],
            timeout=60
        )

    def test_reload_service(self, manager):
        """Test reloading a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.reload("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "reload", "test.service"],
            timeout=30
        )

    def test_enable_service(self, manager):
        """Test enabling a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.enable("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "enable", "test.service"],
            timeout=30
        )

    def test_disable_service(self, manager):
        """Test disabling a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.disable("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "disable", "test.service"],
            timeout=30
        )

    def test_mask_service(self, manager):
        """Test masking a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.mask("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "mask", "test.service"],
            timeout=30
        )

    def test_unmask_service(self, manager):
        """Test unmasking a service."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.unmask("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "systemctl", "unmask", "test.service"],
            timeout=30
        )

    def test_is_active_true(self, manager):
        """Test is_active returns true when service is active."""
        manager._shell.run.return_value = MagicMock(returncode=0)

        result = manager.is_active("test.service")

        assert result is True

    def test_is_active_false(self, manager):
        """Test is_active returns false when service is not active."""
        manager._shell.run.return_value = MagicMock(returncode=3)

        result = manager.is_active("test.service")

        assert result is False

    def test_is_enabled_true(self, manager):
        """Test is_enabled returns true when service is enabled."""
        manager._shell.run.return_value = MagicMock(returncode=0)

        result = manager.is_enabled("test.service")

        assert result is True

    def test_is_enabled_false(self, manager):
        """Test is_enabled returns false when service is not enabled."""
        manager._shell.run.return_value = MagicMock(returncode=1)

        result = manager.is_enabled("test.service")

        assert result is False

    def test_is_failed_true(self, manager):
        """Test is_failed returns true when service is failed."""
        manager._shell.run.return_value = MagicMock(returncode=0)

        result = manager.is_failed("test.service")

        assert result is True

    def test_is_failed_false(self, manager):
        """Test is_failed returns false when service is not failed."""
        manager._shell.run.return_value = MagicMock(returncode=1)

        result = manager.is_failed("test.service")

        assert result is False

    def test_get_status_service(self, manager):
        """Test getting status of a service unit."""
        # Mock the shell calls
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if cmd[1] == "is-active":
                result.stdout = "active"
                result.success = True
            elif cmd[1] == "is-enabled":
                result.stdout = "enabled"
                result.success = True
            elif cmd[1] == "show":
                result.stdout = """Description=Test Service
LoadState=loaded
SubState=running
MainPID=1234
MemoryCurrent=10485760
TasksCurrent=5"""
                result.success = True
            return result

        manager._shell.run.side_effect = mock_run

        status = manager.get_status("test.service")

        assert status.name == "test.service"
        assert status.unit_type == SystemdUnitType.SERVICE
        assert status.active_state == SystemdActiveState.ACTIVE
        assert status.enabled_state == SystemdEnabledState.ENABLED
        assert status.main_pid == 1234
        assert status.memory_current == 10485760

    def test_get_status_timer(self, manager):
        """Test getting status of a timer unit."""
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.stdout = "inactive"
            result.success = True
            return result

        manager._shell.run.side_effect = mock_run

        status = manager.get_status("test.timer")

        assert status.unit_type == SystemdUnitType.TIMER

    def test_get_status_socket(self, manager):
        """Test getting status of a socket unit."""
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.stdout = "inactive"
            result.success = True
            return result

        manager._shell.run.side_effect = mock_run

        status = manager.get_status("test.socket")

        assert status.unit_type == SystemdUnitType.SOCKET

    def test_get_status_unknown_active_state(self, manager):
        """Test handling unknown active state."""
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if "is-active" in cmd:
                result.stdout = "some-unknown-state"
            else:
                result.stdout = "disabled"
            result.success = True
            return result

        manager._shell.run.side_effect = mock_run

        status = manager.get_status("test.service")

        assert status.active_state == SystemdActiveState.UNKNOWN

    def test_get_logs(self, manager):
        """Test getting journal logs."""
        manager._shell.run.return_value = MagicMock(
            success=True,
            stdout="Jan 01 12:00:00 host test[123]: Started\nJan 01 12:00:01 host test[123]: Running"
        )

        logs = manager.get_logs("test.service", lines=50)

        assert len(logs) == 2
        assert "Started" in logs[0]
        assert "Running" in logs[1]

    def test_get_logs_with_filters(self, manager):
        """Test getting logs with time and priority filters."""
        manager._shell.run.return_value = MagicMock(
            success=True,
            stdout="Test log"
        )

        manager.get_logs(
            "test.service",
            lines=100,
            since="1 hour ago",
            until="now",
            priority=4
        )

        call_args = manager._shell.run.call_args[0][0]
        assert "-n" in call_args
        assert "100" in call_args
        assert "--since" in call_args
        assert "1 hour ago" in call_args
        assert "--until" in call_args
        assert "-p" in call_args
        assert "4" in call_args

    def test_get_logs_empty(self, manager):
        """Test getting logs when none available."""
        manager._shell.run.return_value = MagicMock(
            success=False,
            stdout=""
        )

        logs = manager.get_logs("nonexistent.service")

        assert logs == []

    def test_get_logs_json(self, manager):
        """Test getting structured log entries."""
        json_logs = '{"__REALTIME_TIMESTAMP":"1704067200000000","_SYSTEMD_UNIT":"test.service","PRIORITY":"6","MESSAGE":"Started","_PID":"1234","_HOSTNAME":"host"}'
        manager._shell.run.return_value = MagicMock(
            success=True,
            stdout=json_logs
        )

        entries = manager.get_logs_json("test.service", lines=10)

        assert len(entries) == 1
        assert entries[0].unit == "test.service"
        assert entries[0].message == "Started"
        assert entries[0].pid == 1234

    def test_get_logs_json_invalid(self, manager):
        """Test handling invalid JSON in logs."""
        manager._shell.run.return_value = MagicMock(
            success=True,
            stdout="not valid json\n{also not valid"
        )

        entries = manager.get_logs_json("test.service")

        assert entries == []

    def test_clear_logs(self, manager):
        """Test clearing journal logs."""
        manager._shell.run.return_value = MagicMock(success=True)

        result = manager.clear_logs("test.service")

        assert result is True
        manager._shell.run.assert_called_with(
            ["sudo", "journalctl", "--rotate"],
            timeout=30
        )

    def test_unit_exists_true(self, manager):
        """Test unit_exists when unit file exists."""
        with patch.object(Path, 'exists', return_value=True):
            result = manager.unit_exists("test.service")
            assert result is True

    def test_unit_exists_false(self, manager):
        """Test unit_exists when unit file doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            result = manager.unit_exists("nonexistent.service")
            assert result is False

    def test_stop_all_splitwire_services(self, manager):
        """Test stopping all SplitWire services."""
        manager._shell.run.return_value = MagicMock(returncode=0, success=True)

        # Mock is_active to return True for all services
        with patch.object(manager, 'is_active', return_value=True):
            with patch.object(manager, 'stop', return_value=True) as mock_stop:
                result = manager.stop_all_splitwire_services()

        assert result is True
        # Should have called stop for each service
        assert mock_stop.call_count == len(manager.SPLITWIRE_SERVICES)

    def test_get_splitwire_services_status(self, manager):
        """Test getting status of all SplitWire services."""
        mock_status = SystemdUnitStatus(
            name="test",
            unit_type=SystemdUnitType.SERVICE,
            active_state=SystemdActiveState.INACTIVE,
            enabled_state=SystemdEnabledState.DISABLED,
        )

        with patch.object(manager, 'get_status', return_value=mock_status):
            statuses = manager.get_splitwire_services_status()

        assert len(statuses) == len(manager.SPLITWIRE_SERVICES)
        assert "wireguard" in statuses
        assert "zapret" in statuses

    def test_install_splitwire_service_unknown_key(self, manager):
        """Test installing with unknown service key."""
        result = manager.install_splitwire_service("unknown_key")

        assert result is False

    def test_remove_splitwire_service_unknown_key(self, manager):
        """Test removing with unknown service key."""
        result = manager.remove_splitwire_service("unknown_key")

        assert result is False


class TestGetSystemdManager:
    """Tests for the get_systemd_manager singleton function."""

    def test_returns_manager_instance(self):
        """Test that get_systemd_manager returns a SystemdManager."""
        with patch('splitwire.services.systemd.get_logger'), \
             patch('splitwire.services.systemd.get_shell'):
            # Reset singleton
            import splitwire.services.systemd as systemd_module
            systemd_module._systemd_manager = None

            manager = get_systemd_manager()

            assert isinstance(manager, SystemdManager)

    def test_returns_same_instance(self):
        """Test that get_systemd_manager returns singleton."""
        with patch('splitwire.services.systemd.get_logger'), \
             patch('splitwire.services.systemd.get_shell'):
            import splitwire.services.systemd as systemd_module
            systemd_module._systemd_manager = None

            manager1 = get_systemd_manager()
            manager2 = get_systemd_manager()

            assert manager1 is manager2
