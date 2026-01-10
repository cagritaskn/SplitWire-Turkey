"""
Base service class for SplitWire-Turkey Linux.

Provides abstract base class for all services (WireGuard, Zapret, ByeDPI, etc.)
with common interface for installation, removal, and lifecycle management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Callable
import time

from splitwire.core import get_logger, get_shell, CommandResult, CommandStatus


class ServiceStatus(Enum):
    """Status of a service."""
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    REMOVING = "removing"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Type of service for categorization."""
    VPN = "vpn"
    DPI_BYPASS = "dpi_bypass"
    PROXY = "proxy"
    DNS = "dns"
    SYSTEM = "system"


@dataclass
class ServiceInfo:
    """Information about a service."""
    name: str
    display_name: str
    description: str
    service_type: ServiceType
    status: ServiceStatus = ServiceStatus.NOT_INSTALLED
    version: Optional[str] = None
    config_path: Optional[Path] = None
    log_path: Optional[Path] = None
    systemd_unit: Optional[str] = None
    pid: Optional[int] = None
    uptime: Optional[float] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class BaseService(ABC):
    """
    Abstract base class for all services.

    Provides common interface for service lifecycle management:
    - Installation and removal
    - Start, stop, restart
    - Status monitoring
    - Configuration management
    """

    def __init__(self, name: str, display_name: str, description: str,
                 service_type: ServiceType):
        """
        Initialize base service.

        Args:
            name: Internal service name (e.g., 'wireguard', 'zapret')
            display_name: Human-readable name (e.g., 'WireGuard VPN')
            description: Service description
            service_type: Type of service for categorization
        """
        self._name = name
        self._display_name = display_name
        self._description = description
        self._service_type = service_type
        self._logger = get_logger()
        self._shell = get_shell()
        self._status_callbacks: list[Callable[[ServiceStatus], None]] = []

    @property
    def name(self) -> str:
        """Get service name."""
        return self._name

    @property
    def display_name(self) -> str:
        """Get display name."""
        return self._display_name

    @property
    def description(self) -> str:
        """Get service description."""
        return self._description

    @property
    def service_type(self) -> ServiceType:
        """Get service type."""
        return self._service_type

    def add_status_callback(self, callback: Callable[[ServiceStatus], None]) -> None:
        """Add callback for status changes."""
        self._status_callbacks.append(callback)

    def remove_status_callback(self, callback: Callable[[ServiceStatus], None]) -> None:
        """Remove status callback."""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)

    def _notify_status_change(self, status: ServiceStatus) -> None:
        """Notify all callbacks of status change."""
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self._logger.warning(f"Status callback error: {e}")

    # =========================================================================
    # Abstract methods - must be implemented by subclasses
    # =========================================================================

    @abstractmethod
    def install(self, **kwargs) -> bool:
        """
        Install the service.

        Returns:
            True if installation successful
        """
        pass

    @abstractmethod
    def remove(self) -> bool:
        """
        Remove/uninstall the service.

        Returns:
            True if removal successful
        """
        pass

    @abstractmethod
    def start(self) -> bool:
        """
        Start the service.

        Returns:
            True if started successfully
        """
        pass

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the service.

        Returns:
            True if stopped successfully
        """
        pass

    @abstractmethod
    def status(self) -> ServiceStatus:
        """
        Get current service status.

        Returns:
            Current ServiceStatus
        """
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """
        Check if service is installed.

        Returns:
            True if installed
        """
        pass

    # =========================================================================
    # Default implementations - can be overridden
    # =========================================================================

    def restart(self) -> bool:
        """
        Restart the service.

        Default implementation stops then starts.

        Returns:
            True if restarted successfully
        """
        self._logger.info(f"Restarting {self._display_name}")
        if self.is_running():
            if not self.stop():
                return False
            # Brief pause between stop and start
            time.sleep(1)
        return self.start()

    def is_running(self) -> bool:
        """
        Check if service is currently running.

        Returns:
            True if running
        """
        return self.status() == ServiceStatus.RUNNING

    def get_info(self) -> ServiceInfo:
        """
        Get comprehensive service information.

        Returns:
            ServiceInfo with current state
        """
        return ServiceInfo(
            name=self._name,
            display_name=self._display_name,
            description=self._description,
            service_type=self._service_type,
            status=self.status(),
        )

    def enable_autostart(self) -> bool:
        """
        Enable service to start on boot.

        Default implementation uses systemctl enable.

        Returns:
            True if enabled successfully
        """
        systemd_unit = self._get_systemd_unit()
        if not systemd_unit:
            self._logger.warning(f"No systemd unit for {self._name}")
            return False

        result = self._shell.run(
            ["sudo", "systemctl", "enable", systemd_unit],
            timeout=30
        )
        if result.success:
            self._logger.info(f"Enabled autostart for {self._display_name}")
        else:
            self._logger.error(f"Failed to enable autostart: {result.stderr}")
        return result.success

    def disable_autostart(self) -> bool:
        """
        Disable service autostart.

        Returns:
            True if disabled successfully
        """
        systemd_unit = self._get_systemd_unit()
        if not systemd_unit:
            return False

        result = self._shell.run(
            ["sudo", "systemctl", "disable", systemd_unit],
            timeout=30
        )
        if result.success:
            self._logger.info(f"Disabled autostart for {self._display_name}")
        return result.success

    def is_autostart_enabled(self) -> bool:
        """
        Check if autostart is enabled.

        Returns:
            True if enabled
        """
        systemd_unit = self._get_systemd_unit()
        if not systemd_unit:
            return False

        result = self._shell.run(
            ["systemctl", "is-enabled", systemd_unit],
            timeout=10
        )
        return result.success and "enabled" in result.stdout.lower()

    def _get_systemd_unit(self) -> Optional[str]:
        """
        Get the systemd unit name for this service.

        Override in subclass if different from default.

        Returns:
            Systemd unit name or None
        """
        return f"splitwire-{self._name}.service"

    # =========================================================================
    # Helper methods for subclasses
    # =========================================================================

    def _run_privileged(self, command: str | list[str], **kwargs) -> CommandResult:
        """
        Run a command with sudo/pkexec.

        Args:
            command: Command to run
            **kwargs: Additional arguments for shell.run()

        Returns:
            CommandResult
        """
        if isinstance(command, str):
            cmd = f"sudo {command}"
        else:
            cmd = ["sudo"] + command

        return self._shell.run(cmd, **kwargs)

    def _check_binary_exists(self, binary: str) -> bool:
        """
        Check if a binary exists in PATH.

        Args:
            binary: Binary name

        Returns:
            True if exists
        """
        return self._shell.command_exists(binary)

    def _get_binary_path(self, binary: str) -> Optional[str]:
        """
        Get full path to a binary.

        Args:
            binary: Binary name

        Returns:
            Full path or None
        """
        return self._shell.get_command_path(binary)

    def _systemctl(self, action: str, unit: Optional[str] = None) -> CommandResult:
        """
        Run systemctl command.

        Args:
            action: systemctl action (start, stop, status, etc.)
            unit: Unit name (defaults to service's unit)

        Returns:
            CommandResult
        """
        unit = unit or self._get_systemd_unit()
        if not unit:
            return CommandResult(
                status=CommandStatus.FAILED,
                returncode=-1,
                stdout="",
                stderr="No systemd unit configured",
                command=f"systemctl {action}"
            )

        if action in ["start", "stop", "restart", "enable", "disable", "reload"]:
            cmd = ["sudo", "systemctl", action, unit]
        else:
            cmd = ["systemctl", action, unit]

        return self._shell.run(cmd, timeout=30)


class SystemdService(BaseService):
    """
    Base class for services managed by systemd.

    Provides default implementations for systemd-based services.
    """

    def __init__(self, name: str, display_name: str, description: str,
                 service_type: ServiceType, systemd_unit: Optional[str] = None):
        """
        Initialize systemd service.

        Args:
            name: Internal service name
            display_name: Human-readable name
            description: Service description
            service_type: Type of service
            systemd_unit: Custom systemd unit name (optional)
        """
        super().__init__(name, display_name, description, service_type)
        self._systemd_unit = systemd_unit

    def _get_systemd_unit(self) -> Optional[str]:
        """Get systemd unit name."""
        return self._systemd_unit or f"splitwire-{self._name}.service"

    def start(self) -> bool:
        """Start the systemd service."""
        self._logger.info(f"Starting {self._display_name}")

        result = self._systemctl("start")
        if result.success:
            self._logger.info(f"{self._display_name} started")
            self._notify_status_change(ServiceStatus.RUNNING)
            return True
        else:
            self._logger.error(f"Failed to start {self._display_name}: {result.stderr}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def stop(self) -> bool:
        """Stop the systemd service."""
        self._logger.info(f"Stopping {self._display_name}")

        result = self._systemctl("stop")
        if result.success:
            self._logger.info(f"{self._display_name} stopped")
            self._notify_status_change(ServiceStatus.STOPPED)
            return True
        else:
            self._logger.error(f"Failed to stop {self._display_name}: {result.stderr}")
            return False

    def status(self) -> ServiceStatus:
        """Get systemd service status."""
        if not self.is_installed():
            return ServiceStatus.NOT_INSTALLED

        result = self._systemctl("is-active")
        stdout = result.stdout.strip().lower()

        if stdout == "active":
            return ServiceStatus.RUNNING
        elif stdout == "inactive":
            return ServiceStatus.STOPPED
        elif stdout == "failed":
            return ServiceStatus.FAILED
        else:
            return ServiceStatus.UNKNOWN

    def is_installed(self) -> bool:
        """Check if systemd unit file exists."""
        unit = self._get_systemd_unit()
        if not unit:
            return False

        # Check if unit file exists
        result = self._shell.run(
            ["systemctl", "list-unit-files", unit],
            timeout=10
        )
        return unit in result.stdout


if __name__ == "__main__":
    # Test the base service classes
    print("=" * 50)
    print("BaseService Test")
    print("=" * 50)

    print("\nServiceStatus values:")
    for status in ServiceStatus:
        print(f"  {status.name}: {status.value}")

    print("\nServiceType values:")
    for stype in ServiceType:
        print(f"  {stype.name}: {stype.value}")

    print("\nServiceInfo example:")
    info = ServiceInfo(
        name="test",
        display_name="Test Service",
        description="A test service",
        service_type=ServiceType.SYSTEM,
        status=ServiceStatus.STOPPED,
    )
    print(f"  Name: {info.name}")
    print(f"  Display: {info.display_name}")
    print(f"  Status: {info.status.value}")

    print("\nTest completed!")
