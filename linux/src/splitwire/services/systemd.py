"""
SplitWire-Turkey systemd Service Manager.

Provides comprehensive systemd integration for managing services:
- Install/remove service unit files
- Enable/disable autostart
- Start/stop/restart services
- Check service status
- Read journal logs
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Callable
import os
import tempfile
import shutil

from splitwire.core import get_logger, get_shell, CommandResult


class SystemdUnitType(Enum):
    """Type of systemd unit."""
    SERVICE = "service"
    TIMER = "timer"
    SOCKET = "socket"
    PATH = "path"


class SystemdActiveState(Enum):
    """Active state of a systemd unit."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    RELOADING = "reloading"
    UNKNOWN = "unknown"


class SystemdEnabledState(Enum):
    """Enabled state of a systemd unit."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    STATIC = "static"
    MASKED = "masked"
    INDIRECT = "indirect"
    UNKNOWN = "unknown"


@dataclass
class SystemdUnitStatus:
    """Status information for a systemd unit."""
    name: str
    unit_type: SystemdUnitType
    active_state: SystemdActiveState
    enabled_state: SystemdEnabledState
    description: str = ""
    load_state: str = "not-found"
    sub_state: str = ""
    main_pid: Optional[int] = None
    memory_current: Optional[int] = None  # bytes
    tasks_current: Optional[int] = None
    cpu_usage_nsec: Optional[int] = None
    invocation_id: Optional[str] = None
    active_enter_timestamp: Optional[str] = None
    inactive_enter_timestamp: Optional[str] = None

    @property
    def is_running(self) -> bool:
        """Check if unit is running."""
        return self.active_state == SystemdActiveState.ACTIVE

    @property
    def is_enabled(self) -> bool:
        """Check if unit is enabled."""
        return self.enabled_state == SystemdEnabledState.ENABLED

    @property
    def is_failed(self) -> bool:
        """Check if unit has failed."""
        return self.active_state == SystemdActiveState.FAILED


@dataclass
class JournalEntry:
    """A journal log entry."""
    timestamp: str
    unit: str
    priority: int
    message: str
    pid: Optional[int] = None
    hostname: Optional[str] = None


class SystemdManager:
    """
    Manager for systemd services.

    Provides comprehensive systemd integration including:
    - Unit file management (install, remove, reload)
    - Service lifecycle (start, stop, restart, reload)
    - Status monitoring
    - Journal log access
    """

    # System paths
    SYSTEM_UNIT_DIR = Path("/etc/systemd/system")
    USER_UNIT_DIR = Path.home() / ".config/systemd/user"

    # SplitWire service unit names
    SPLITWIRE_SERVICES = {
        "wireguard": "splitwire-wg.service",
        "wireguard-refresh": "splitwire-wg-refresh.timer",
        "zapret": "splitwire-zapret.service",
        "byedpi": "splitwire-byedpi.service",
        "cgproxy": "splitwire-cgproxy.service",
    }

    def __init__(self):
        """Initialize systemd manager."""
        self._logger = get_logger()
        self._shell = get_shell()
        self._unit_files_dir = Path(__file__).parent.parent.parent.parent / "systemd"

    # =========================================================================
    # Unit File Management
    # =========================================================================

    def install_unit(self, unit_name: str, content: Optional[str] = None,
                     enable: bool = True, start: bool = False) -> bool:
        """
        Install a systemd unit file.

        Args:
            unit_name: Name of the unit (e.g., 'splitwire-wg.service')
            content: Unit file content (if None, reads from bundled files)
            enable: Whether to enable the unit
            start: Whether to start the unit after installation

        Returns:
            True if installation successful
        """
        self._logger.info(f"Installing systemd unit: {unit_name}")

        # Get unit content
        if content is None:
            content = self._get_bundled_unit_content(unit_name)
            if content is None:
                self._logger.error(f"No bundled unit file found for: {unit_name}")
                return False

        # Write to temp file first
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.service',
                                             delete=False) as f:
                f.write(content)
                temp_path = f.name

            # Copy to system directory
            target_path = self.SYSTEM_UNIT_DIR / unit_name
            result = self._shell.run(
                ["sudo", "cp", temp_path, str(target_path)],
                timeout=30
            )

            # Clean up temp file
            os.unlink(temp_path)

            if not result.success:
                self._logger.error(f"Failed to copy unit file: {result.stderr}")
                return False

            # Set permissions
            self._shell.run(
                ["sudo", "chmod", "644", str(target_path)],
                timeout=10
            )

            # Reload systemd
            self.daemon_reload()

            # Enable if requested
            if enable:
                self.enable(unit_name)

            # Start if requested
            if start:
                self.start(unit_name)

            self._logger.info(f"Successfully installed: {unit_name}")
            return True

        except Exception as e:
            self._logger.error(f"Error installing unit: {e}")
            return False

    def remove_unit(self, unit_name: str, stop_first: bool = True) -> bool:
        """
        Remove a systemd unit file.

        Args:
            unit_name: Name of the unit to remove
            stop_first: Whether to stop the service first

        Returns:
            True if removal successful
        """
        self._logger.info(f"Removing systemd unit: {unit_name}")

        # Stop the service first
        if stop_first:
            self.stop(unit_name)
            self.disable(unit_name)

        # Remove unit file
        target_path = self.SYSTEM_UNIT_DIR / unit_name
        if target_path.exists():
            result = self._shell.run(
                ["sudo", "rm", "-f", str(target_path)],
                timeout=30
            )
            if not result.success:
                self._logger.error(f"Failed to remove unit file: {result.stderr}")
                return False

        # Reload systemd
        self.daemon_reload()

        # Reset failed state if any
        self._shell.run(
            ["sudo", "systemctl", "reset-failed", unit_name],
            timeout=10
        )

        self._logger.info(f"Successfully removed: {unit_name}")
        return True

    def unit_exists(self, unit_name: str) -> bool:
        """
        Check if a unit file exists.

        Args:
            unit_name: Name of the unit

        Returns:
            True if unit exists
        """
        target_path = self.SYSTEM_UNIT_DIR / unit_name
        return target_path.exists()

    def daemon_reload(self) -> bool:
        """
        Reload systemd daemon to pick up unit file changes.

        Returns:
            True if successful
        """
        result = self._shell.run(
            ["sudo", "systemctl", "daemon-reload"],
            timeout=30
        )
        if not result.success:
            self._logger.error(f"daemon-reload failed: {result.stderr}")
        return result.success

    def _get_bundled_unit_content(self, unit_name: str) -> Optional[str]:
        """Get content of bundled unit file."""
        unit_path = self._unit_files_dir / unit_name
        if unit_path.exists():
            return unit_path.read_text()
        return None

    # =========================================================================
    # Service Lifecycle
    # =========================================================================

    def start(self, unit_name: str) -> bool:
        """
        Start a systemd unit.

        Args:
            unit_name: Name of the unit

        Returns:
            True if started successfully
        """
        self._logger.info(f"Starting: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "start", unit_name],
            timeout=60
        )
        if not result.success:
            self._logger.error(f"Failed to start {unit_name}: {result.stderr}")
        return result.success

    def stop(self, unit_name: str) -> bool:
        """
        Stop a systemd unit.

        Args:
            unit_name: Name of the unit

        Returns:
            True if stopped successfully
        """
        self._logger.info(f"Stopping: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "stop", unit_name],
            timeout=60
        )
        if not result.success:
            # Don't log error if service wasn't running
            if "not loaded" not in result.stderr.lower():
                self._logger.error(f"Failed to stop {unit_name}: {result.stderr}")
        return result.success

    def restart(self, unit_name: str) -> bool:
        """
        Restart a systemd unit.

        Args:
            unit_name: Name of the unit

        Returns:
            True if restarted successfully
        """
        self._logger.info(f"Restarting: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "restart", unit_name],
            timeout=60
        )
        if not result.success:
            self._logger.error(f"Failed to restart {unit_name}: {result.stderr}")
        return result.success

    def reload(self, unit_name: str) -> bool:
        """
        Reload a systemd unit (send SIGHUP).

        Args:
            unit_name: Name of the unit

        Returns:
            True if reloaded successfully
        """
        self._logger.info(f"Reloading: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "reload", unit_name],
            timeout=30
        )
        if not result.success:
            self._logger.error(f"Failed to reload {unit_name}: {result.stderr}")
        return result.success

    def enable(self, unit_name: str) -> bool:
        """
        Enable a systemd unit (start on boot).

        Args:
            unit_name: Name of the unit

        Returns:
            True if enabled successfully
        """
        self._logger.info(f"Enabling: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "enable", unit_name],
            timeout=30
        )
        if not result.success:
            self._logger.error(f"Failed to enable {unit_name}: {result.stderr}")
        return result.success

    def disable(self, unit_name: str) -> bool:
        """
        Disable a systemd unit (don't start on boot).

        Args:
            unit_name: Name of the unit

        Returns:
            True if disabled successfully
        """
        self._logger.info(f"Disabling: {unit_name}")
        result = self._shell.run(
            ["sudo", "systemctl", "disable", unit_name],
            timeout=30
        )
        if not result.success:
            # Don't log error if already disabled
            if "does not exist" not in result.stderr.lower():
                self._logger.error(f"Failed to disable {unit_name}: {result.stderr}")
        return result.success

    def mask(self, unit_name: str) -> bool:
        """
        Mask a systemd unit (prevent starting).

        Args:
            unit_name: Name of the unit

        Returns:
            True if masked successfully
        """
        result = self._shell.run(
            ["sudo", "systemctl", "mask", unit_name],
            timeout=30
        )
        return result.success

    def unmask(self, unit_name: str) -> bool:
        """
        Unmask a systemd unit.

        Args:
            unit_name: Name of the unit

        Returns:
            True if unmasked successfully
        """
        result = self._shell.run(
            ["sudo", "systemctl", "unmask", unit_name],
            timeout=30
        )
        return result.success

    # =========================================================================
    # Status Monitoring
    # =========================================================================

    def get_status(self, unit_name: str) -> SystemdUnitStatus:
        """
        Get detailed status of a systemd unit.

        Args:
            unit_name: Name of the unit

        Returns:
            SystemdUnitStatus with current state
        """
        # Determine unit type
        if unit_name.endswith('.timer'):
            unit_type = SystemdUnitType.TIMER
        elif unit_name.endswith('.socket'):
            unit_type = SystemdUnitType.SOCKET
        elif unit_name.endswith('.path'):
            unit_type = SystemdUnitType.PATH
        else:
            unit_type = SystemdUnitType.SERVICE

        # Get active state
        active_result = self._shell.run(
            ["systemctl", "is-active", unit_name],
            timeout=10
        )
        active_str = active_result.stdout.strip().lower()
        try:
            active_state = SystemdActiveState(active_str)
        except ValueError:
            active_state = SystemdActiveState.UNKNOWN

        # Get enabled state
        enabled_result = self._shell.run(
            ["systemctl", "is-enabled", unit_name],
            timeout=10
        )
        enabled_str = enabled_result.stdout.strip().lower()
        try:
            enabled_state = SystemdEnabledState(enabled_str)
        except ValueError:
            enabled_state = SystemdEnabledState.UNKNOWN

        # Get additional info via show
        status = SystemdUnitStatus(
            name=unit_name,
            unit_type=unit_type,
            active_state=active_state,
            enabled_state=enabled_state,
        )

        # Parse detailed status
        show_result = self._shell.run(
            ["systemctl", "show", unit_name,
             "--property=Description,LoadState,SubState,MainPID,"
             "MemoryCurrent,TasksCurrent,CPUUsageNSec,InvocationID,"
             "ActiveEnterTimestamp,InactiveEnterTimestamp"],
            timeout=10
        )

        if show_result.success:
            for line in show_result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key == "Description":
                        status.description = value
                    elif key == "LoadState":
                        status.load_state = value
                    elif key == "SubState":
                        status.sub_state = value
                    elif key == "MainPID" and value.isdigit():
                        status.main_pid = int(value)
                    elif key == "MemoryCurrent" and value.isdigit():
                        status.memory_current = int(value)
                    elif key == "TasksCurrent" and value.isdigit():
                        status.tasks_current = int(value)
                    elif key == "CPUUsageNSec" and value.isdigit():
                        status.cpu_usage_nsec = int(value)
                    elif key == "InvocationID" and value:
                        status.invocation_id = value
                    elif key == "ActiveEnterTimestamp" and value:
                        status.active_enter_timestamp = value
                    elif key == "InactiveEnterTimestamp" and value:
                        status.inactive_enter_timestamp = value

        return status

    def is_active(self, unit_name: str) -> bool:
        """
        Check if a unit is active (running).

        Args:
            unit_name: Name of the unit

        Returns:
            True if active
        """
        result = self._shell.run(
            ["systemctl", "is-active", "--quiet", unit_name],
            timeout=10
        )
        return result.returncode == 0

    def is_enabled(self, unit_name: str) -> bool:
        """
        Check if a unit is enabled.

        Args:
            unit_name: Name of the unit

        Returns:
            True if enabled
        """
        result = self._shell.run(
            ["systemctl", "is-enabled", "--quiet", unit_name],
            timeout=10
        )
        return result.returncode == 0

    def is_failed(self, unit_name: str) -> bool:
        """
        Check if a unit is in failed state.

        Args:
            unit_name: Name of the unit

        Returns:
            True if failed
        """
        result = self._shell.run(
            ["systemctl", "is-failed", "--quiet", unit_name],
            timeout=10
        )
        return result.returncode == 0

    # =========================================================================
    # Journal Logs
    # =========================================================================

    def get_logs(self, unit_name: str, lines: int = 100,
                 since: Optional[str] = None, until: Optional[str] = None,
                 priority: Optional[int] = None) -> List[str]:
        """
        Get journal logs for a unit.

        Args:
            unit_name: Name of the unit
            lines: Maximum number of lines to return
            since: Start time (e.g., '1 hour ago', '2024-01-01')
            until: End time
            priority: Maximum priority level (0-7)

        Returns:
            List of log lines
        """
        cmd = ["journalctl", "-u", unit_name, "-n", str(lines), "--no-pager"]

        if since:
            cmd.extend(["--since", since])
        if until:
            cmd.extend(["--until", until])
        if priority is not None:
            cmd.extend(["-p", str(priority)])

        result = self._shell.run(cmd, timeout=30)

        if result.success:
            return result.stdout.strip().split('\n')
        return []

    def get_logs_json(self, unit_name: str, lines: int = 100) -> List[JournalEntry]:
        """
        Get journal logs as structured entries.

        Args:
            unit_name: Name of the unit
            lines: Maximum number of entries

        Returns:
            List of JournalEntry objects
        """
        import json

        result = self._shell.run(
            ["journalctl", "-u", unit_name, "-n", str(lines),
             "--no-pager", "-o", "json"],
            timeout=30
        )

        entries = []
        if result.success:
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(JournalEntry(
                        timestamp=data.get("__REALTIME_TIMESTAMP", ""),
                        unit=data.get("_SYSTEMD_UNIT", unit_name),
                        priority=int(data.get("PRIORITY", 6)),
                        message=data.get("MESSAGE", ""),
                        pid=int(data.get("_PID", 0)) or None,
                        hostname=data.get("_HOSTNAME"),
                    ))
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return entries

    def follow_logs(self, unit_name: str, callback: Callable[[str], None]) -> None:
        """
        Follow journal logs in real-time (blocking).

        Args:
            unit_name: Name of the unit
            callback: Function to call with each log line
        """
        # Note: This is blocking. For async use, run in a thread
        import subprocess

        proc = subprocess.Popen(
            ["journalctl", "-u", unit_name, "-f", "--no-pager"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            for line in proc.stdout:
                callback(line.rstrip())
        except KeyboardInterrupt:
            proc.terminate()

    def clear_logs(self, unit_name: str) -> bool:
        """
        Clear journal logs for a unit (requires root).

        Args:
            unit_name: Name of the unit

        Returns:
            True if successful
        """
        # journalctl doesn't support clearing per-unit, so we rotate and vacuum
        result = self._shell.run(
            ["sudo", "journalctl", "--rotate"],
            timeout=30
        )
        return result.success

    # =========================================================================
    # SplitWire-specific helpers
    # =========================================================================

    def get_splitwire_services_status(self) -> Dict[str, SystemdUnitStatus]:
        """
        Get status of all SplitWire services.

        Returns:
            Dict mapping service key to status
        """
        status_dict = {}
        for key, unit_name in self.SPLITWIRE_SERVICES.items():
            status_dict[key] = self.get_status(unit_name)
        return status_dict

    def install_splitwire_service(self, service_key: str,
                                   config: Optional[Dict] = None) -> bool:
        """
        Install a SplitWire service.

        Args:
            service_key: Key from SPLITWIRE_SERVICES
            config: Optional configuration to substitute in unit file

        Returns:
            True if successful
        """
        unit_name = self.SPLITWIRE_SERVICES.get(service_key)
        if not unit_name:
            self._logger.error(f"Unknown service key: {service_key}")
            return False

        return self.install_unit(unit_name, enable=True)

    def remove_splitwire_service(self, service_key: str) -> bool:
        """
        Remove a SplitWire service.

        Args:
            service_key: Key from SPLITWIRE_SERVICES

        Returns:
            True if successful
        """
        unit_name = self.SPLITWIRE_SERVICES.get(service_key)
        if not unit_name:
            return False

        return self.remove_unit(unit_name)

    def stop_all_splitwire_services(self) -> bool:
        """
        Stop all SplitWire services.

        Returns:
            True if all stopped successfully
        """
        success = True
        for unit_name in self.SPLITWIRE_SERVICES.values():
            if self.is_active(unit_name):
                if not self.stop(unit_name):
                    success = False
        return success

    def remove_all_splitwire_services(self) -> bool:
        """
        Remove all SplitWire services.

        Returns:
            True if all removed successfully
        """
        success = True
        for unit_name in self.SPLITWIRE_SERVICES.values():
            if self.unit_exists(unit_name):
                if not self.remove_unit(unit_name):
                    success = False
        return success


# Singleton instance
_systemd_manager: Optional[SystemdManager] = None


def get_systemd_manager() -> SystemdManager:
    """Get the singleton SystemdManager instance."""
    global _systemd_manager
    if _systemd_manager is None:
        _systemd_manager = SystemdManager()
    return _systemd_manager


if __name__ == "__main__":
    # Test the systemd manager
    print("=" * 50)
    print("SystemdManager Test")
    print("=" * 50)

    manager = get_systemd_manager()

    print("\nSplitWire services:")
    for key, unit in manager.SPLITWIRE_SERVICES.items():
        print(f"  {key}: {unit}")

    print("\nChecking service status...")
    for key, unit in manager.SPLITWIRE_SERVICES.items():
        status = manager.get_status(unit)
        print(f"  {unit}:")
        print(f"    Active: {status.active_state.value}")
        print(f"    Enabled: {status.enabled_state.value}")

    print("\nTest completed!")
