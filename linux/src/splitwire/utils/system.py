"""
System detection and compatibility checking module.

Detects Ubuntu version, systemd, firewall backend, WireGuard support,
and other system capabilities needed for SplitWire-Turkey.
"""

import os
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class FirewallBackend(Enum):
    """Detected firewall backend."""
    IPTABLES = "iptables"
    NFTABLES = "nftables"
    FIREWALLD = "firewalld"
    UNKNOWN = "unknown"


class InitSystem(Enum):
    """Detected init system."""
    SYSTEMD = "systemd"
    OPENRC = "openrc"
    SYSVINIT = "sysvinit"
    UNKNOWN = "unknown"


class DNSManager(Enum):
    """Detected DNS manager."""
    SYSTEMD_RESOLVED = "systemd-resolved"
    NETWORK_MANAGER = "NetworkManager"
    RESOLVCONF = "resolvconf"
    MANUAL = "manual"
    UNKNOWN = "unknown"


@dataclass
class UbuntuVersion:
    """Ubuntu version information."""
    version: str = ""
    codename: str = ""
    major: int = 0
    minor: int = 0
    is_ubuntu: bool = False
    is_supported: bool = False

    def __str__(self) -> str:
        if self.is_ubuntu:
            return f"Ubuntu {self.version} ({self.codename})"
        return "Not Ubuntu"


@dataclass
class SystemInfo:
    """Complete system information."""
    # OS info
    ubuntu: UbuntuVersion = field(default_factory=UbuntuVersion)
    kernel_version: str = ""
    architecture: str = ""

    # Init system
    init_system: InitSystem = InitSystem.UNKNOWN

    # Firewall
    firewall_backend: FirewallBackend = FirewallBackend.UNKNOWN
    iptables_available: bool = False
    nftables_available: bool = False

    # WireGuard
    wireguard_module_loaded: bool = False
    wireguard_tools_installed: bool = False
    wg_quick_available: bool = False

    # NFQUEUE (for zapret)
    nfqueue_available: bool = False
    libnetfilter_queue_installed: bool = False

    # DNS
    dns_manager: DNSManager = DNSManager.UNKNOWN
    resolvectl_available: bool = False

    # cgroups (for app-based routing)
    cgroups_v2: bool = False
    cgproxy_available: bool = False

    # Python
    python_version: str = ""
    python_major: int = 0
    python_minor: int = 0

    # User
    is_root: bool = False
    can_sudo: bool = False

    def is_compatible(self) -> bool:
        """Check if system is compatible with SplitWire-Turkey."""
        return (
            self.ubuntu.is_supported and
            self.init_system == InitSystem.SYSTEMD and
            self.python_major >= 3 and
            self.python_minor >= 10
        )

    def get_compatibility_issues(self) -> list[str]:
        """Get list of compatibility issues."""
        issues = []

        if not self.ubuntu.is_ubuntu:
            issues.append("Not running Ubuntu (other distros not yet supported)")
        elif not self.ubuntu.is_supported:
            issues.append(f"Ubuntu {self.ubuntu.version} not supported (requires 22.04+)")

        if self.init_system != InitSystem.SYSTEMD:
            issues.append("systemd not detected (required for service management)")

        if self.python_major < 3 or (self.python_major == 3 and self.python_minor < 10):
            issues.append(f"Python {self.python_version} not supported (requires 3.10+)")

        if not self.wireguard_tools_installed:
            issues.append("WireGuard tools not installed")

        if not self.nfqueue_available:
            issues.append("NFQUEUE not available (required for Zapret)")

        return issues


class SystemDetector:
    """Detects system capabilities and compatibility."""

    def __init__(self):
        self._info: Optional[SystemInfo] = None

    def detect(self) -> SystemInfo:
        """Run full system detection."""
        self._info = SystemInfo()

        self._detect_ubuntu_version()
        self._detect_kernel()
        self._detect_architecture()
        self._detect_init_system()
        self._detect_firewall()
        self._detect_wireguard()
        self._detect_nfqueue()
        self._detect_dns_manager()
        self._detect_cgroups()
        self._detect_python()
        self._detect_user_privileges()

        return self._info

    def _run_command(self, cmd: list[str], timeout: int = 5) -> tuple[int, str, str]:
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

    def _command_exists(self, cmd: str) -> bool:
        """Check if a command exists in PATH."""
        code, _, _ = self._run_command(["which", cmd])
        return code == 0

    def _detect_ubuntu_version(self) -> None:
        """Detect Ubuntu version from /etc/os-release."""
        os_release = Path("/etc/os-release")

        if not os_release.exists():
            return

        try:
            content = os_release.read_text()
            info = {}
            for line in content.splitlines():
                if "=" in line:
                    key, _, value = line.partition("=")
                    info[key] = value.strip('"')

            distro_id = info.get("ID", "").lower()

            if distro_id == "ubuntu":
                self._info.ubuntu.is_ubuntu = True
                self._info.ubuntu.version = info.get("VERSION_ID", "")
                self._info.ubuntu.codename = info.get("VERSION_CODENAME", "")

                # Parse version
                if self._info.ubuntu.version:
                    parts = self._info.ubuntu.version.split(".")
                    if len(parts) >= 1:
                        self._info.ubuntu.major = int(parts[0])
                    if len(parts) >= 2:
                        self._info.ubuntu.minor = int(parts[1])

                # Check if supported (22.04+)
                if self._info.ubuntu.major >= 22:
                    self._info.ubuntu.is_supported = True
                elif self._info.ubuntu.major == 22 and self._info.ubuntu.minor >= 4:
                    self._info.ubuntu.is_supported = True
        except Exception:
            pass

    def _detect_kernel(self) -> None:
        """Detect kernel version."""
        code, stdout, _ = self._run_command(["uname", "-r"])
        if code == 0:
            self._info.kernel_version = stdout

    def _detect_architecture(self) -> None:
        """Detect system architecture."""
        code, stdout, _ = self._run_command(["uname", "-m"])
        if code == 0:
            self._info.architecture = stdout

    def _detect_init_system(self) -> None:
        """Detect init system (systemd, openrc, etc.)."""
        # Check for systemd
        if Path("/run/systemd/system").exists():
            self._info.init_system = InitSystem.SYSTEMD
            return

        # Check for OpenRC
        if Path("/run/openrc").exists():
            self._info.init_system = InitSystem.OPENRC
            return

        # Check PID 1
        try:
            pid1 = Path("/proc/1/comm").read_text().strip()
            if pid1 == "systemd":
                self._info.init_system = InitSystem.SYSTEMD
            elif pid1 == "init":
                self._info.init_system = InitSystem.SYSVINIT
        except Exception:
            pass

    def _detect_firewall(self) -> None:
        """Detect firewall backend."""
        # Check iptables
        self._info.iptables_available = self._command_exists("iptables")

        # Check nftables
        self._info.nftables_available = self._command_exists("nft")

        # Check firewalld
        if self._command_exists("firewall-cmd"):
            code, _, _ = self._run_command(["systemctl", "is-active", "firewalld"])
            if code == 0:
                self._info.firewall_backend = FirewallBackend.FIREWALLD
                return

        # Determine primary backend
        # On Ubuntu, iptables is usually the default
        if self._info.iptables_available:
            # Check if iptables is actually nftables backend
            code, stdout, _ = self._run_command(["iptables", "--version"])
            if code == 0 and "nf_tables" in stdout:
                self._info.firewall_backend = FirewallBackend.NFTABLES
            else:
                self._info.firewall_backend = FirewallBackend.IPTABLES
        elif self._info.nftables_available:
            self._info.firewall_backend = FirewallBackend.NFTABLES

    def _detect_wireguard(self) -> None:
        """Detect WireGuard support."""
        # Check if module is loaded
        code, stdout, _ = self._run_command(["lsmod"])
        if code == 0:
            self._info.wireguard_module_loaded = "wireguard" in stdout

        # Also check /sys/module
        if Path("/sys/module/wireguard").exists():
            self._info.wireguard_module_loaded = True

        # Check wireguard-tools
        self._info.wg_quick_available = self._command_exists("wg-quick")
        self._info.wireguard_tools_installed = self._command_exists("wg")

    def _detect_nfqueue(self) -> None:
        """Detect NFQUEUE support for Zapret."""
        # Check if NFQUEUE target is available
        # Try to list iptables extensions
        code, stdout, _ = self._run_command(
            ["iptables", "-m", "nfqueue", "--help"],
            timeout=3
        )
        # If help text is shown, NFQUEUE is available
        self._info.nfqueue_available = code == 0 or "NFQUEUE" in stdout

        # Check for libnetfilter-queue
        # Look for the library file
        lib_paths = [
            "/usr/lib/x86_64-linux-gnu/libnetfilter_queue.so",
            "/usr/lib/libnetfilter_queue.so",
            "/lib/x86_64-linux-gnu/libnetfilter_queue.so",
        ]
        self._info.libnetfilter_queue_installed = any(
            Path(p).exists() or Path(p + ".1").exists()
            for p in lib_paths
        )

    def _detect_dns_manager(self) -> None:
        """Detect DNS manager."""
        # Check for systemd-resolved
        code, _, _ = self._run_command(["systemctl", "is-active", "systemd-resolved"])
        if code == 0:
            self._info.dns_manager = DNSManager.SYSTEMD_RESOLVED
            self._info.resolvectl_available = self._command_exists("resolvectl")
            return

        # Check for NetworkManager
        code, _, _ = self._run_command(["systemctl", "is-active", "NetworkManager"])
        if code == 0:
            self._info.dns_manager = DNSManager.NETWORK_MANAGER
            return

        # Check for resolvconf
        if self._command_exists("resolvconf"):
            self._info.dns_manager = DNSManager.RESOLVCONF
            return

        # Manual (direct /etc/resolv.conf editing)
        if Path("/etc/resolv.conf").exists():
            self._info.dns_manager = DNSManager.MANUAL

    def _detect_cgroups(self) -> None:
        """Detect cgroups version and cgproxy availability."""
        # Check cgroups v2
        if Path("/sys/fs/cgroup/cgroup.controllers").exists():
            self._info.cgroups_v2 = True

        # Check cgproxy
        self._info.cgproxy_available = self._command_exists("cgproxy")

    def _detect_python(self) -> None:
        """Detect Python version."""
        import sys
        self._info.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self._info.python_major = sys.version_info.major
        self._info.python_minor = sys.version_info.minor

    def _detect_user_privileges(self) -> None:
        """Detect user privileges."""
        self._info.is_root = os.geteuid() == 0

        # Check if user can sudo
        if not self._info.is_root:
            code, _, _ = self._run_command(["sudo", "-n", "true"])
            self._info.can_sudo = code == 0


def get_system_info() -> SystemInfo:
    """Get system information (convenience function)."""
    detector = SystemDetector()
    return detector.detect()


def print_system_info(info: SystemInfo) -> None:
    """Print system information in a formatted way."""
    print("=" * 50)
    print("SplitWire-Turkey System Information")
    print("=" * 50)

    print(f"\nOS: {info.ubuntu}")
    print(f"Kernel: {info.kernel_version}")
    print(f"Architecture: {info.architecture}")

    print(f"\nInit System: {info.init_system.value}")
    print(f"Firewall: {info.firewall_backend.value}")
    print(f"  - iptables: {'Yes' if info.iptables_available else 'No'}")
    print(f"  - nftables: {'Yes' if info.nftables_available else 'No'}")

    print(f"\nWireGuard:")
    print(f"  - Module loaded: {'Yes' if info.wireguard_module_loaded else 'No'}")
    print(f"  - Tools installed: {'Yes' if info.wireguard_tools_installed else 'No'}")
    print(f"  - wg-quick: {'Yes' if info.wg_quick_available else 'No'}")

    print(f"\nNFQUEUE (Zapret):")
    print(f"  - Available: {'Yes' if info.nfqueue_available else 'No'}")
    print(f"  - libnetfilter-queue: {'Yes' if info.libnetfilter_queue_installed else 'No'}")

    print(f"\nDNS Manager: {info.dns_manager.value}")
    print(f"  - resolvectl: {'Yes' if info.resolvectl_available else 'No'}")

    print(f"\ncgroups:")
    print(f"  - v2: {'Yes' if info.cgroups_v2 else 'No'}")
    print(f"  - cgproxy: {'Yes' if info.cgproxy_available else 'No'}")

    print(f"\nPython: {info.python_version}")
    print(f"Running as root: {'Yes' if info.is_root else 'No'}")
    print(f"Can sudo: {'Yes' if info.can_sudo else 'N/A' if info.is_root else 'No'}")

    print("\n" + "=" * 50)
    if info.is_compatible():
        print("System is COMPATIBLE with SplitWire-Turkey")
    else:
        print("System has COMPATIBILITY ISSUES:")
        for issue in info.get_compatibility_issues():
            print(f"  - {issue}")
    print("=" * 50)


if __name__ == "__main__":
    # Test the system detector
    info = get_system_info()
    print_system_info(info)
