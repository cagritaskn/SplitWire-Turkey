"""
Polkit (PolicyKit) helper module for privilege escalation.

Provides wrappers around pkexec for running commands with elevated
privileges from a GUI application.
"""

import os
import subprocess
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Callable


class ElevationMethod(Enum):
    """Method for privilege elevation."""
    PKEXEC = "pkexec"       # Polkit (GUI dialog)
    SUDO = "sudo"           # sudo (terminal)
    GKSUDO = "gksudo"       # Legacy GTK sudo
    KDESUDO = "kdesudo"     # KDE sudo
    ROOT = "root"           # Already root
    NONE = "none"           # No elevation available


@dataclass
class ElevationResult:
    """Result of an elevated command execution."""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    cancelled: bool = False  # True if user cancelled auth dialog
    method: ElevationMethod = ElevationMethod.NONE


class PolkitError(Exception):
    """Exception raised for polkit-related errors."""
    pass


class PolkitHelper:
    """
    Helper class for running commands with elevated privileges.

    Uses pkexec (Polkit) for GUI applications, with fallbacks to sudo.
    """

    # Action IDs for our polkit policy
    ACTION_WIREGUARD = "com.splitwire.turkey.wireguard"
    ACTION_ZAPRET = "com.splitwire.turkey.zapret"
    ACTION_DNS = "com.splitwire.turkey.dns"
    ACTION_SYSTEM = "com.splitwire.turkey.system"

    # Path to our polkit policy file
    POLICY_PATH = "/usr/share/polkit-1/actions/com.splitwire.turkey.policy"

    def __init__(self):
        self._elevation_method: Optional[ElevationMethod] = None
        self._is_root = os.geteuid() == 0

    @property
    def is_root(self) -> bool:
        """Check if running as root."""
        return self._is_root

    @property
    def elevation_method(self) -> ElevationMethod:
        """Get the available elevation method."""
        if self._elevation_method is None:
            self._elevation_method = self._detect_elevation_method()
        return self._elevation_method

    def _detect_elevation_method(self) -> ElevationMethod:
        """Detect the best available elevation method."""
        if self._is_root:
            return ElevationMethod.ROOT

        # Check pkexec (preferred for GUI)
        if shutil.which("pkexec"):
            return ElevationMethod.PKEXEC

        # Check sudo
        if shutil.which("sudo"):
            return ElevationMethod.SUDO

        # Legacy options
        if shutil.which("gksudo"):
            return ElevationMethod.GKSUDO

        if shutil.which("kdesudo"):
            return ElevationMethod.KDESUDO

        return ElevationMethod.NONE

    def can_elevate(self) -> bool:
        """Check if privilege elevation is available."""
        return self.elevation_method != ElevationMethod.NONE

    def is_policy_installed(self) -> bool:
        """Check if our polkit policy is installed."""
        return Path(self.POLICY_PATH).exists()

    def run_elevated(
        self,
        command: list[str],
        action_id: Optional[str] = None,
        timeout: int = 60,
        capture_output: bool = True
    ) -> ElevationResult:
        """
        Run a command with elevated privileges.

        Args:
            command: Command and arguments to run
            action_id: Polkit action ID (for pkexec)
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            ElevationResult with command output and status
        """
        method = self.elevation_method

        if method == ElevationMethod.ROOT:
            # Already root, run directly
            return self._run_direct(command, timeout, capture_output)

        if method == ElevationMethod.PKEXEC:
            return self._run_pkexec(command, action_id, timeout, capture_output)

        if method == ElevationMethod.SUDO:
            return self._run_sudo(command, timeout, capture_output)

        if method in (ElevationMethod.GKSUDO, ElevationMethod.KDESUDO):
            return self._run_legacy_sudo(command, method, timeout, capture_output)

        return ElevationResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="No elevation method available",
            method=ElevationMethod.NONE
        )

    def _run_direct(
        self,
        command: list[str],
        timeout: int,
        capture_output: bool
    ) -> ElevationResult:
        """Run command directly (when already root)."""
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return ElevationResult(
                    success=result.returncode == 0,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    method=ElevationMethod.ROOT
                )
            else:
                result = subprocess.run(command, timeout=timeout)
                return ElevationResult(
                    success=result.returncode == 0,
                    returncode=result.returncode,
                    stdout="",
                    stderr="",
                    method=ElevationMethod.ROOT
                )
        except subprocess.TimeoutExpired:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Command timed out",
                method=ElevationMethod.ROOT
            )
        except Exception as e:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                method=ElevationMethod.ROOT
            )

    def _run_pkexec(
        self,
        command: list[str],
        action_id: Optional[str],
        timeout: int,
        capture_output: bool
    ) -> ElevationResult:
        """Run command with pkexec."""
        # Build pkexec command
        pkexec_cmd = ["pkexec"]

        # Note: pkexec doesn't support --action directly for arbitrary commands
        # The action ID is determined by the policy file based on the command
        pkexec_cmd.extend(command)

        try:
            if capture_output:
                result = subprocess.run(
                    pkexec_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=self._get_pkexec_env()
                )
            else:
                result = subprocess.run(
                    pkexec_cmd,
                    timeout=timeout,
                    env=self._get_pkexec_env()
                )
                return ElevationResult(
                    success=result.returncode == 0,
                    returncode=result.returncode,
                    stdout="",
                    stderr="",
                    method=ElevationMethod.PKEXEC
                )

            # Check for user cancellation (pkexec returns 126 when cancelled)
            cancelled = result.returncode == 126

            return ElevationResult(
                success=result.returncode == 0,
                returncode=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                cancelled=cancelled,
                method=ElevationMethod.PKEXEC
            )

        except subprocess.TimeoutExpired:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Command timed out",
                method=ElevationMethod.PKEXEC
            )
        except Exception as e:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                method=ElevationMethod.PKEXEC
            )

    def _run_sudo(
        self,
        command: list[str],
        timeout: int,
        capture_output: bool
    ) -> ElevationResult:
        """Run command with sudo."""
        sudo_cmd = ["sudo"] + command

        try:
            if capture_output:
                result = subprocess.run(
                    sudo_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(sudo_cmd, timeout=timeout)
                return ElevationResult(
                    success=result.returncode == 0,
                    returncode=result.returncode,
                    stdout="",
                    stderr="",
                    method=ElevationMethod.SUDO
                )

            return ElevationResult(
                success=result.returncode == 0,
                returncode=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                method=ElevationMethod.SUDO
            )

        except subprocess.TimeoutExpired:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Command timed out",
                method=ElevationMethod.SUDO
            )
        except Exception as e:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                method=ElevationMethod.SUDO
            )

    def _run_legacy_sudo(
        self,
        command: list[str],
        method: ElevationMethod,
        timeout: int,
        capture_output: bool
    ) -> ElevationResult:
        """Run command with gksudo or kdesudo."""
        if method == ElevationMethod.GKSUDO:
            sudo_cmd = ["gksudo", "--"] + command
        else:
            sudo_cmd = ["kdesudo", "--"] + command

        try:
            if capture_output:
                result = subprocess.run(
                    sudo_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(sudo_cmd, timeout=timeout)
                return ElevationResult(
                    success=result.returncode == 0,
                    returncode=result.returncode,
                    stdout="",
                    stderr="",
                    method=method
                )

            return ElevationResult(
                success=result.returncode == 0,
                returncode=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                method=method
            )

        except subprocess.TimeoutExpired:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Command timed out",
                method=method
            )
        except Exception as e:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                method=method
            )

    def _get_pkexec_env(self) -> dict:
        """Get environment variables for pkexec."""
        env = os.environ.copy()
        # pkexec needs DISPLAY for GUI dialogs
        if "DISPLAY" not in env:
            env["DISPLAY"] = ":0"
        return env

    # Convenience methods for common operations

    def run_wg_quick(self, action: str, interface: str) -> ElevationResult:
        """Run wg-quick up/down."""
        return self.run_elevated(
            ["wg-quick", action, interface],
            action_id=self.ACTION_WIREGUARD,
            timeout=30
        )

    def run_systemctl(self, action: str, service: str) -> ElevationResult:
        """Run systemctl action on a service."""
        return self.run_elevated(
            ["systemctl", action, service],
            action_id=self.ACTION_SYSTEM,
            timeout=30
        )

    def run_iptables(self, args: list[str]) -> ElevationResult:
        """Run iptables command."""
        return self.run_elevated(
            ["iptables"] + args,
            action_id=self.ACTION_ZAPRET,
            timeout=10
        )

    def copy_file_as_root(self, src: str, dst: str) -> ElevationResult:
        """Copy a file to a root-owned location."""
        return self.run_elevated(
            ["cp", src, dst],
            action_id=self.ACTION_SYSTEM,
            timeout=10
        )

    def write_file_as_root(self, content: str, path: str) -> ElevationResult:
        """Write content to a root-owned file using tee."""
        # Use tee to write to file
        try:
            proc = subprocess.Popen(
                ["pkexec", "tee", path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._get_pkexec_env()
            )
            stdout, stderr = proc.communicate(input=content, timeout=30)

            return ElevationResult(
                success=proc.returncode == 0,
                returncode=proc.returncode,
                stdout=stdout,
                stderr=stderr,
                cancelled=proc.returncode == 126,
                method=ElevationMethod.PKEXEC
            )
        except Exception as e:
            return ElevationResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                method=ElevationMethod.PKEXEC
            )


# Global instance for convenience
_polkit_helper: Optional[PolkitHelper] = None


def get_polkit_helper() -> PolkitHelper:
    """Get the global PolkitHelper instance."""
    global _polkit_helper
    if _polkit_helper is None:
        _polkit_helper = PolkitHelper()
    return _polkit_helper


def run_elevated(command: list[str], **kwargs) -> ElevationResult:
    """Run a command with elevated privileges (convenience function)."""
    return get_polkit_helper().run_elevated(command, **kwargs)


def can_elevate() -> bool:
    """Check if privilege elevation is available (convenience function)."""
    return get_polkit_helper().can_elevate()


def is_root() -> bool:
    """Check if running as root (convenience function)."""
    return get_polkit_helper().is_root


if __name__ == "__main__":
    # Test the polkit helper
    helper = PolkitHelper()

    print("=" * 50)
    print("Polkit Helper Test")
    print("=" * 50)
    print(f"Running as root: {helper.is_root}")
    print(f"Elevation method: {helper.elevation_method.value}")
    print(f"Can elevate: {helper.can_elevate()}")
    print(f"Policy installed: {helper.is_policy_installed()}")

    if not helper.is_root and helper.can_elevate():
        print("\nTesting elevated command (whoami)...")
        result = helper.run_elevated(["whoami"])
        print(f"Success: {result.success}")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.cancelled:
            print("(User cancelled authentication)")
