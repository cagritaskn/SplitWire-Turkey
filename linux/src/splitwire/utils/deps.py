"""
Dependency checking and installation module.

Checks for required system packages and Python dependencies,
and provides installation commands/automation.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DependencyStatus(Enum):
    """Status of a dependency."""
    INSTALLED = "installed"
    MISSING = "missing"
    OUTDATED = "outdated"
    UNKNOWN = "unknown"


class PackageManager(Enum):
    """Available package managers."""
    APT = "apt"
    SNAP = "snap"
    FLATPAK = "flatpak"
    PIP = "pip"


@dataclass
class Dependency:
    """Represents a system or Python dependency."""
    name: str
    package_name: str  # apt package name
    description: str
    required: bool = True
    status: DependencyStatus = DependencyStatus.UNKNOWN
    version: str = ""
    check_command: list[str] = field(default_factory=list)
    install_command: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status_icon = {
            DependencyStatus.INSTALLED: "[OK]",
            DependencyStatus.MISSING: "[!!]",
            DependencyStatus.OUTDATED: "[UP]",
            DependencyStatus.UNKNOWN: "[??]",
        }
        req = "*" if self.required else " "
        return f"{status_icon[self.status]} {req} {self.name}: {self.description}"


# Required system packages for SplitWire-Turkey
SYSTEM_DEPENDENCIES: list[Dependency] = [
    # GTK4 and Libadwaita
    Dependency(
        name="python3-gi",
        package_name="python3-gi",
        description="Python GObject introspection",
        required=True,
        check_command=["python3", "-c", "import gi"],
    ),
    Dependency(
        name="python3-gi-cairo",
        package_name="python3-gi-cairo",
        description="Python GObject Cairo bindings",
        required=True,
        check_command=["python3", "-c", "import gi; gi.require_version('cairo', '1.0')"],
    ),
    Dependency(
        name="GTK4",
        package_name="gir1.2-gtk-4.0",
        description="GTK4 GObject introspection",
        required=True,
        check_command=["python3", "-c", "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk"],
    ),
    Dependency(
        name="Libadwaita",
        package_name="gir1.2-adw-1",
        description="Libadwaita for GNOME styling",
        required=True,
        check_command=["python3", "-c", "import gi; gi.require_version('Adw', '1'); from gi.repository import Adw"],
    ),

    # WireGuard
    Dependency(
        name="wireguard-tools",
        package_name="wireguard-tools",
        description="WireGuard userspace tools (wg, wg-quick)",
        required=True,
        check_command=["which", "wg-quick"],
    ),

    # Zapret dependencies
    Dependency(
        name="libnetfilter-queue-dev",
        package_name="libnetfilter-queue-dev",
        description="Netfilter queue library (for Zapret nfqws)",
        required=True,
        check_command=["dpkg", "-s", "libnetfilter-queue-dev"],
    ),
    Dependency(
        name="iptables",
        package_name="iptables",
        description="IP packet filter administration",
        required=True,
        check_command=["which", "iptables"],
    ),

    # cgroups for app-based routing
    Dependency(
        name="cgroup-tools",
        package_name="cgroup-tools",
        description="Control group tools",
        required=False,  # Optional, for advanced features
        check_command=["which", "cgcreate"],
    ),

    # General utilities
    Dependency(
        name="curl",
        package_name="curl",
        description="Command line HTTP client",
        required=True,
        check_command=["which", "curl"],
    ),
    Dependency(
        name="wget",
        package_name="wget",
        description="Network downloader",
        required=False,
        check_command=["which", "wget"],
    ),
    Dependency(
        name="git",
        package_name="git",
        description="Version control (for Zapret clone)",
        required=True,
        check_command=["which", "git"],
    ),

    # Polkit for GUI privilege elevation
    Dependency(
        name="policykit-1",
        package_name="policykit-1",
        description="PolicyKit authentication agent",
        required=True,
        check_command=["which", "pkexec"],
    ),
]


# Python dependencies (from pip)
PYTHON_DEPENDENCIES: list[Dependency] = [
    Dependency(
        name="httpx",
        package_name="httpx",
        description="Modern HTTP client for API calls",
        required=True,
        check_command=["python3", "-c", "import httpx"],
    ),
    Dependency(
        name="pydantic",
        package_name="pydantic",
        description="Data validation library",
        required=True,
        check_command=["python3", "-c", "import pydantic"],
    ),
]


class DependencyChecker:
    """Checks and manages system and Python dependencies."""

    def __init__(self):
        self.system_deps = [Dependency(**d.__dict__) for d in SYSTEM_DEPENDENCIES]
        self.python_deps = [Dependency(**d.__dict__) for d in PYTHON_DEPENDENCIES]
        self._apt_available: Optional[bool] = None

    def _run_command(self, cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "Command not found"
        except Exception as e:
            return -1, "", str(e)

    def _is_apt_available(self) -> bool:
        """Check if apt is available."""
        if self._apt_available is None:
            code, _, _ = self._run_command(["which", "apt"])
            self._apt_available = code == 0
        return self._apt_available

    def check_all(self) -> tuple[list[Dependency], list[Dependency]]:
        """
        Check all dependencies.

        Returns:
            Tuple of (system_deps, python_deps) with updated status
        """
        self.check_system_dependencies()
        self.check_python_dependencies()
        return self.system_deps, self.python_deps

    def check_system_dependencies(self) -> list[Dependency]:
        """Check all system dependencies."""
        for dep in self.system_deps:
            if dep.check_command:
                code, _, _ = self._run_command(dep.check_command)
                dep.status = (
                    DependencyStatus.INSTALLED if code == 0
                    else DependencyStatus.MISSING
                )
            else:
                dep.status = DependencyStatus.UNKNOWN
        return self.system_deps

    def check_python_dependencies(self) -> list[Dependency]:
        """Check all Python dependencies."""
        for dep in self.python_deps:
            if dep.check_command:
                code, _, _ = self._run_command(dep.check_command)
                dep.status = (
                    DependencyStatus.INSTALLED if code == 0
                    else DependencyStatus.MISSING
                )
            else:
                dep.status = DependencyStatus.UNKNOWN
        return self.python_deps

    def get_missing_system_deps(self) -> list[Dependency]:
        """Get list of missing system dependencies."""
        return [d for d in self.system_deps if d.status == DependencyStatus.MISSING]

    def get_missing_python_deps(self) -> list[Dependency]:
        """Get list of missing Python dependencies."""
        return [d for d in self.python_deps if d.status == DependencyStatus.MISSING]

    def get_missing_required_deps(self) -> list[Dependency]:
        """Get list of missing required dependencies (both system and Python)."""
        missing = []
        missing.extend([d for d in self.system_deps if d.status == DependencyStatus.MISSING and d.required])
        missing.extend([d for d in self.python_deps if d.status == DependencyStatus.MISSING and d.required])
        return missing

    def get_apt_install_command(self) -> list[str]:
        """Get the apt install command for missing system dependencies."""
        missing = self.get_missing_system_deps()
        if not missing:
            return []

        packages = [d.package_name for d in missing]
        return ["sudo", "apt", "install", "-y"] + packages

    def get_pip_install_command(self) -> list[str]:
        """Get the pip install command for missing Python dependencies."""
        missing = self.get_missing_python_deps()
        if not missing:
            return []

        packages = [d.package_name for d in missing]
        return [sys.executable, "-m", "pip", "install"] + packages

    def install_system_dependencies(self, interactive: bool = True) -> bool:
        """
        Install missing system dependencies using apt.

        Args:
            interactive: If True, asks for confirmation

        Returns:
            True if installation succeeded or nothing to install
        """
        missing = self.get_missing_system_deps()
        if not missing:
            return True

        if not self._is_apt_available():
            print("Error: apt package manager not available")
            return False

        packages = [d.package_name for d in missing]
        print(f"Missing system packages: {', '.join(packages)}")

        if interactive:
            response = input("Install missing packages? [Y/n]: ").strip().lower()
            if response and response != 'y':
                return False

        cmd = ["sudo", "apt", "update"]
        print(f"Running: {' '.join(cmd)}")
        code, _, _ = self._run_command(cmd, timeout=120)
        if code != 0:
            print("Warning: apt update failed, continuing anyway...")

        cmd = ["sudo", "apt", "install", "-y"] + packages
        print(f"Running: {' '.join(cmd)}")

        # For installation, we need to run interactively
        try:
            result = subprocess.run(cmd, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing packages: {e}")
            return False

    def install_python_dependencies(self, interactive: bool = True) -> bool:
        """
        Install missing Python dependencies using pip.

        Args:
            interactive: If True, asks for confirmation

        Returns:
            True if installation succeeded or nothing to install
        """
        missing = self.get_missing_python_deps()
        if not missing:
            return True

        packages = [d.package_name for d in missing]
        print(f"Missing Python packages: {', '.join(packages)}")

        if interactive:
            response = input("Install missing packages? [Y/n]: ").strip().lower()
            if response and response != 'y':
                return False

        cmd = [sys.executable, "-m", "pip", "install"] + packages
        print(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, timeout=120)
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing packages: {e}")
            return False

    def check_python_version(self) -> tuple[bool, str]:
        """
        Check if Python version is compatible.

        Returns:
            Tuple of (is_compatible, message)
        """
        major, minor = sys.version_info[:2]
        version_str = f"{major}.{minor}.{sys.version_info.micro}"

        if major < 3 or (major == 3 and minor < 10):
            return False, f"Python {version_str} not supported. Requires Python 3.10+"
        return True, f"Python {version_str} is compatible"


def check_dependencies() -> tuple[list[Dependency], list[Dependency]]:
    """Check all dependencies (convenience function)."""
    checker = DependencyChecker()
    return checker.check_all()


def print_dependency_status(system_deps: list[Dependency], python_deps: list[Dependency]) -> None:
    """Print dependency status in a formatted way."""
    print("=" * 50)
    print("SplitWire-Turkey Dependency Check")
    print("=" * 50)

    print("\nSystem Dependencies:")
    print("-" * 40)
    for dep in system_deps:
        print(f"  {dep}")

    print("\nPython Dependencies:")
    print("-" * 40)
    for dep in python_deps:
        print(f"  {dep}")

    # Summary
    missing_sys = [d for d in system_deps if d.status == DependencyStatus.MISSING]
    missing_py = [d for d in python_deps if d.status == DependencyStatus.MISSING]

    print("\n" + "=" * 50)
    if not missing_sys and not missing_py:
        print("All dependencies are installed!")
    else:
        if missing_sys:
            print(f"Missing system packages: {len(missing_sys)}")
            print(f"  Install with: sudo apt install {' '.join(d.package_name for d in missing_sys)}")
        if missing_py:
            print(f"Missing Python packages: {len(missing_py)}")
            print(f"  Install with: pip install {' '.join(d.package_name for d in missing_py)}")
    print("=" * 50)


def install_all_dependencies(interactive: bool = True) -> bool:
    """
    Check and install all missing dependencies.

    Args:
        interactive: If True, asks for confirmation before installing

    Returns:
        True if all dependencies are satisfied
    """
    checker = DependencyChecker()
    checker.check_all()

    # Check Python version first
    compatible, msg = checker.check_python_version()
    print(msg)
    if not compatible:
        return False

    # Print current status
    print_dependency_status(checker.system_deps, checker.python_deps)

    # Install missing
    if checker.get_missing_system_deps():
        if not checker.install_system_dependencies(interactive):
            print("Failed to install system dependencies")
            return False
        # Re-check
        checker.check_system_dependencies()

    if checker.get_missing_python_deps():
        if not checker.install_python_dependencies(interactive):
            print("Failed to install Python dependencies")
            return False
        # Re-check
        checker.check_python_dependencies()

    # Final check
    missing = checker.get_missing_required_deps()
    if missing:
        print(f"\nStill missing required dependencies: {', '.join(d.name for d in missing)}")
        return False

    print("\nAll dependencies satisfied!")
    return True


if __name__ == "__main__":
    # Test the dependency checker
    system_deps, python_deps = check_dependencies()
    print_dependency_status(system_deps, python_deps)
