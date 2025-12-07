"""
DNS management service for SplitWire-Turkey Linux.

Provides DNS configuration with DoH (DNS over HTTPS) support.
Uses systemd-resolved for Ubuntu systems.
"""

import json
import subprocess
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime

from splitwire.core import get_logger, get_shell
from splitwire.services.base import BaseService, ServiceStatus, ServiceType


# ============================================================================
# Constants
# ============================================================================

# Configuration paths
LOCAL_CONFIG_DIR = Path.home() / ".config" / "splitwire" / "dns"
CONFIG_FILE = LOCAL_CONFIG_DIR / "config.json"
BACKUP_FILE = LOCAL_CONFIG_DIR / "backup.json"

# systemd-resolved paths
RESOLVED_CONF = Path("/etc/systemd/resolved.conf")
RESOLVED_CONF_DIR = Path("/etc/systemd/resolved.conf.d")
SPLITWIRE_RESOLVED_CONF = RESOLVED_CONF_DIR / "splitwire.conf"

# Network Manager paths (fallback)
NM_CONF_DIR = Path("/etc/NetworkManager/conf.d")


class DNSManager(Enum):
    """DNS management backend."""
    SYSTEMD_RESOLVED = "systemd-resolved"  # Primary for Ubuntu
    NETWORK_MANAGER = "networkmanager"      # Alternative
    RESOLVCONF = "resolvconf"               # Legacy
    MANUAL = "manual"                        # Direct /etc/resolv.conf edit
    UNKNOWN = "unknown"


class DoHMode(Enum):
    """DNS over HTTPS mode."""
    OFF = "off"                    # No DoH
    OPPORTUNISTIC = "opportunistic"  # Use DoH if available
    STRICT = "strict"              # Require DoH, fail if unavailable


@dataclass
class DNSServer:
    """DNS server configuration."""
    name: str
    primary: str
    secondary: str
    doh_url: Optional[str] = None
    dot_hostname: Optional[str] = None  # DNS over TLS hostname


@dataclass
class DNSBackup:
    """Backup of original DNS settings."""
    timestamp: str
    dns_servers: list[str]
    search_domains: list[str]
    doh_enabled: bool
    interface: Optional[str] = None
    raw_config: Optional[str] = None


@dataclass
class DNSConfig:
    """DNS service configuration."""
    enabled: bool = False
    preset_name: str = "cloudflare"
    custom_primary: str = ""
    custom_secondary: str = ""
    doh_mode: DoHMode = DoHMode.OPPORTUNISTIC
    auto_apply_on_install: bool = False
    backup_exists: bool = False


# ============================================================================
# DNS Presets
# ============================================================================

DNS_PRESETS: dict[str, DNSServer] = {
    "google": DNSServer(
        name="Google DNS",
        primary="8.8.8.8",
        secondary="8.8.4.4",
        doh_url="https://dns.google/dns-query",
        dot_hostname="dns.google",
    ),
    "cloudflare": DNSServer(
        name="Cloudflare DNS",
        primary="1.1.1.1",
        secondary="1.0.0.1",
        doh_url="https://cloudflare-dns.com/dns-query",
        dot_hostname="cloudflare-dns.com",
    ),
    "cloudflare_family": DNSServer(
        name="Cloudflare Family",
        primary="1.1.1.3",
        secondary="1.0.0.3",
        doh_url="https://family.cloudflare-dns.com/dns-query",
        dot_hostname="family.cloudflare-dns.com",
    ),
    "quad9": DNSServer(
        name="Quad9 DNS",
        primary="9.9.9.9",
        secondary="149.112.112.112",
        doh_url="https://dns.quad9.net/dns-query",
        dot_hostname="dns.quad9.net",
    ),
    "quad9_unsecured": DNSServer(
        name="Quad9 Unsecured",
        primary="9.9.9.10",
        secondary="149.112.112.10",
        doh_url="https://dns10.quad9.net/dns-query",
        dot_hostname="dns10.quad9.net",
    ),
    "opendns": DNSServer(
        name="OpenDNS",
        primary="208.67.222.222",
        secondary="208.67.220.220",
        doh_url="https://doh.opendns.com/dns-query",
        dot_hostname="dns.opendns.com",
    ),
    "adguard": DNSServer(
        name="AdGuard DNS",
        primary="94.140.14.14",
        secondary="94.140.15.15",
        doh_url="https://dns.adguard-dns.com/dns-query",
        dot_hostname="dns.adguard-dns.com",
    ),
    "adguard_family": DNSServer(
        name="AdGuard Family",
        primary="94.140.14.15",
        secondary="94.140.15.16",
        doh_url="https://family.adguard-dns.com/dns-query",
        dot_hostname="family.adguard-dns.com",
    ),
    "turkish_telecom": DNSServer(
        name="Turk Telekom DNS",
        primary="195.175.39.39",
        secondary="195.175.39.40",
        doh_url=None,  # No DoH support
        dot_hostname=None,
    ),
}


class DNSService(BaseService):
    """
    DNS management service.

    Provides DNS configuration with DoH support using systemd-resolved
    on Ubuntu systems. Supports multiple DNS presets and custom servers.

    Features:
    - Multiple DNS presets (Google, Cloudflare, Quad9, etc.)
    - DNS over HTTPS (DoH) support
    - DNS over TLS (DoT) support
    - Backup and restore original DNS settings
    - Auto-apply DNS on service installation
    """

    def __init__(self):
        """Initialize DNS service."""
        super().__init__(
            name="dns",
            display_name="DNS Service",
            description="DNS management with DoH support",
            service_type=ServiceType.DNS,
        )
        self._config = DNSConfig()
        self._dns_manager: Optional[DNSManager] = None
        self._ensure_directories()
        self._load_config()
        self._detect_dns_manager()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        LOCAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                self._config = DNSConfig(
                    enabled=data.get("enabled", False),
                    preset_name=data.get("preset_name", "cloudflare"),
                    custom_primary=data.get("custom_primary", ""),
                    custom_secondary=data.get("custom_secondary", ""),
                    doh_mode=DoHMode(data.get("doh_mode", "opportunistic")),
                    auto_apply_on_install=data.get("auto_apply_on_install", False),
                    backup_exists=data.get("backup_exists", False),
                )
            except Exception as e:
                self._logger.warning(f"Failed to load config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        data = {
            "enabled": self._config.enabled,
            "preset_name": self._config.preset_name,
            "custom_primary": self._config.custom_primary,
            "custom_secondary": self._config.custom_secondary,
            "doh_mode": self._config.doh_mode.value,
            "auto_apply_on_install": self._config.auto_apply_on_install,
            "backup_exists": self._config.backup_exists,
        }
        CONFIG_FILE.write_text(json.dumps(data, indent=2))

    def _detect_dns_manager(self) -> None:
        """Detect which DNS manager is in use."""
        # Check for systemd-resolved (primary for Ubuntu)
        result = self._shell.run(["systemctl", "is-active", "systemd-resolved"], timeout=5)
        if result.success and result.stdout.strip() == "active":
            self._dns_manager = DNSManager.SYSTEMD_RESOLVED
            self._logger.info("Detected DNS manager: systemd-resolved")
            return

        # Check for NetworkManager
        result = self._shell.run(["systemctl", "is-active", "NetworkManager"], timeout=5)
        if result.success and result.stdout.strip() == "active":
            self._dns_manager = DNSManager.NETWORK_MANAGER
            self._logger.info("Detected DNS manager: NetworkManager")
            return

        # Check for resolvconf
        if self._shell.command_exists("resolvconf"):
            self._dns_manager = DNSManager.RESOLVCONF
            self._logger.info("Detected DNS manager: resolvconf")
            return

        # Fallback to manual
        self._dns_manager = DNSManager.MANUAL
        self._logger.warning("No supported DNS manager found, using manual mode")

    # =========================================================================
    # BaseService implementation
    # =========================================================================

    def install(self, preset: Optional[str] = None,
                primary: Optional[str] = None,
                secondary: Optional[str] = None,
                doh_mode: DoHMode = DoHMode.OPPORTUNISTIC,
                **kwargs) -> bool:
        """
        Install DNS configuration.

        Args:
            preset: DNS preset name (google, cloudflare, quad9, etc.)
            primary: Custom primary DNS (overrides preset)
            secondary: Custom secondary DNS (overrides preset)
            doh_mode: DNS over HTTPS mode

        Returns:
            True if installation successful
        """
        self._logger.info("Installing DNS configuration")
        self._notify_status_change(ServiceStatus.INSTALLING)

        try:
            # Backup current settings first
            if not self._config.backup_exists:
                self._backup_current_dns()

            # Determine DNS servers to use
            if primary:
                dns_primary = primary
                dns_secondary = secondary or primary
                self._config.custom_primary = primary
                self._config.custom_secondary = secondary or ""
            elif preset and preset in DNS_PRESETS:
                dns_server = DNS_PRESETS[preset]
                dns_primary = dns_server.primary
                dns_secondary = dns_server.secondary
                self._config.preset_name = preset
            else:
                # Use default preset
                dns_server = DNS_PRESETS["cloudflare"]
                dns_primary = dns_server.primary
                dns_secondary = dns_server.secondary

            self._config.doh_mode = doh_mode

            # Apply DNS settings based on detected manager
            if self._dns_manager == DNSManager.SYSTEMD_RESOLVED:
                if not self._apply_systemd_resolved(dns_primary, dns_secondary, doh_mode):
                    return False
            elif self._dns_manager == DNSManager.NETWORK_MANAGER:
                if not self._apply_network_manager(dns_primary, dns_secondary):
                    return False
            else:
                if not self._apply_manual(dns_primary, dns_secondary):
                    return False

            self._config.enabled = True
            self._save_config()

            self._logger.info(f"DNS configured: {dns_primary}, {dns_secondary}")
            self._notify_status_change(ServiceStatus.RUNNING)
            return True

        except Exception as e:
            self._logger.exception(f"DNS installation failed: {e}")
            self._notify_status_change(ServiceStatus.FAILED)
            return False

    def remove(self) -> bool:
        """Remove DNS configuration and restore original settings."""
        self._logger.info("Removing DNS configuration")

        try:
            # Restore original settings
            if self._config.backup_exists:
                self._restore_dns()

            self._config.enabled = False
            self._save_config()

            self._logger.info("DNS configuration removed")
            self._notify_status_change(ServiceStatus.NOT_INSTALLED)
            return True

        except Exception as e:
            self._logger.exception(f"DNS removal failed: {e}")
            return False

    def start(self) -> bool:
        """Start/apply DNS configuration."""
        if not self._config.enabled:
            return self.install()
        return True

    def stop(self) -> bool:
        """Stop DNS configuration (restore original)."""
        return self.remove()

    def status(self) -> ServiceStatus:
        """Get DNS service status."""
        if not self._config.enabled:
            return ServiceStatus.NOT_INSTALLED

        # Verify DNS is actually configured
        current_dns = self._get_current_dns()
        if current_dns:
            preset = self.get_current_preset()
            if preset:
                if preset.primary in current_dns or preset.secondary in current_dns:
                    return ServiceStatus.RUNNING

            # Check custom DNS
            if self._config.custom_primary and self._config.custom_primary in current_dns:
                return ServiceStatus.RUNNING

        return ServiceStatus.STOPPED

    def is_installed(self) -> bool:
        """Check if DNS is configured."""
        return self._config.enabled

    # =========================================================================
    # DNS specific methods
    # =========================================================================

    def get_config(self) -> DNSConfig:
        """Get current configuration."""
        return self._config

    def get_dns_manager(self) -> DNSManager:
        """Get detected DNS manager."""
        return self._dns_manager or DNSManager.UNKNOWN

    def get_all_presets(self) -> dict[str, DNSServer]:
        """Get all available DNS presets."""
        return DNS_PRESETS.copy()

    def get_preset(self, name: str) -> Optional[DNSServer]:
        """Get a specific preset by name."""
        return DNS_PRESETS.get(name)

    def get_current_preset(self) -> Optional[DNSServer]:
        """Get the currently selected preset."""
        return self.get_preset(self._config.preset_name)

    def set_preset(self, name: str) -> bool:
        """Set the active DNS preset."""
        if name not in DNS_PRESETS:
            self._logger.error(f"Unknown preset: {name}")
            return False

        self._config.preset_name = name
        self._config.custom_primary = ""
        self._config.custom_secondary = ""
        self._save_config()
        return True

    def set_custom_dns(self, primary: str, secondary: str = "") -> None:
        """Set custom DNS servers."""
        self._config.custom_primary = primary
        self._config.custom_secondary = secondary
        self._save_config()

    def set_doh_mode(self, mode: DoHMode) -> None:
        """Set DNS over HTTPS mode."""
        self._config.doh_mode = mode
        self._save_config()

    def set_auto_apply(self, enabled: bool) -> None:
        """Set auto-apply DNS on install option."""
        self._config.auto_apply_on_install = enabled
        self._save_config()

    def get_current_dns(self) -> list[str]:
        """Get currently configured DNS servers."""
        return self._get_current_dns()

    def is_doh_enabled(self) -> bool:
        """Check if DoH is currently enabled."""
        if self._dns_manager == DNSManager.SYSTEMD_RESOLVED:
            result = self._shell.run(
                ["resolvectl", "status"],
                timeout=10
            )
            if result.success:
                return "DNSOverTLS" in result.stdout and "yes" in result.stdout.lower()
        return False

    def restore_original(self) -> bool:
        """Restore original DNS settings from backup."""
        return self._restore_dns()

    def has_backup(self) -> bool:
        """Check if backup exists."""
        return self._config.backup_exists and BACKUP_FILE.exists()

    def should_auto_apply(self) -> bool:
        """Check if DNS should be auto-applied on service install."""
        return self._config.auto_apply_on_install

    def apply_if_auto(self) -> bool:
        """Apply DNS if auto-apply is enabled."""
        if self.should_auto_apply() and not self._config.enabled:
            return self.install()
        return True

    # =========================================================================
    # systemd-resolved methods
    # =========================================================================

    def _apply_systemd_resolved(self, primary: str, secondary: str,
                                 doh_mode: DoHMode) -> bool:
        """Apply DNS using systemd-resolved."""
        self._logger.info("Applying DNS via systemd-resolved")

        try:
            # Create resolved.conf.d directory if needed
            result = self._run_privileged(["mkdir", "-p", str(RESOLVED_CONF_DIR)])
            if not result.success:
                self._logger.error(f"Failed to create config dir: {result.stderr}")
                return False

            # Get DoH/DoT settings
            preset = self.get_current_preset()
            dot_hostname = preset.dot_hostname if preset else None

            # Build resolved.conf content
            config_lines = [
                "# Generated by SplitWire-Turkey",
                "# Do not edit manually",
                "[Resolve]",
                f"DNS={primary} {secondary}",
                "FallbackDNS=1.1.1.1 8.8.8.8",
                "Domains=~.",
                "DNSSEC=allow-downgrade",
            ]

            # Add DoT/DoH settings
            if doh_mode == DoHMode.STRICT:
                config_lines.append("DNSOverTLS=yes")
            elif doh_mode == DoHMode.OPPORTUNISTIC:
                config_lines.append("DNSOverTLS=opportunistic")
            else:
                config_lines.append("DNSOverTLS=no")

            config_content = "\n".join(config_lines) + "\n"

            # Write config file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
                f.write(config_content)
                tmp_path = f.name

            result = self._run_privileged(["cp", tmp_path, str(SPLITWIRE_RESOLVED_CONF)])
            Path(tmp_path).unlink(missing_ok=True)

            if not result.success:
                self._logger.error(f"Failed to write config: {result.stderr}")
                return False

            # Set permissions
            self._run_privileged(["chmod", "644", str(SPLITWIRE_RESOLVED_CONF)])

            # Restart systemd-resolved
            result = self._run_privileged(["systemctl", "restart", "systemd-resolved"])
            if not result.success:
                self._logger.error(f"Failed to restart resolved: {result.stderr}")
                return False

            self._logger.info("systemd-resolved configured successfully")
            return True

        except Exception as e:
            self._logger.exception(f"Failed to apply systemd-resolved: {e}")
            return False

    def _remove_systemd_resolved(self) -> bool:
        """Remove systemd-resolved configuration."""
        try:
            if SPLITWIRE_RESOLVED_CONF.exists():
                self._run_privileged(["rm", "-f", str(SPLITWIRE_RESOLVED_CONF)])

            # Restart to apply default settings
            self._run_privileged(["systemctl", "restart", "systemd-resolved"])
            return True

        except Exception as e:
            self._logger.warning(f"Failed to remove resolved config: {e}")
            return False

    # =========================================================================
    # NetworkManager methods
    # =========================================================================

    def _apply_network_manager(self, primary: str, secondary: str) -> bool:
        """Apply DNS using NetworkManager."""
        self._logger.info("Applying DNS via NetworkManager")

        try:
            # Get active connection
            result = self._shell.run(
                ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"],
                timeout=10
            )
            if not result.success:
                self._logger.error("Failed to get active connections")
                return False

            connections = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        connections.append(parts[0])

            if not connections:
                self._logger.error("No active network connections")
                return False

            # Apply DNS to each connection
            for conn in connections:
                result = self._run_privileged([
                    "nmcli", "connection", "modify", conn,
                    "ipv4.dns", f"{primary} {secondary}",
                    "ipv4.ignore-auto-dns", "yes"
                ])
                if not result.success:
                    self._logger.warning(f"Failed to modify connection {conn}")

            # Restart NetworkManager
            self._run_privileged(["systemctl", "restart", "NetworkManager"])

            return True

        except Exception as e:
            self._logger.exception(f"Failed to apply NetworkManager DNS: {e}")
            return False

    # =========================================================================
    # Manual /etc/resolv.conf methods
    # =========================================================================

    def _apply_manual(self, primary: str, secondary: str) -> bool:
        """Apply DNS by directly editing /etc/resolv.conf."""
        self._logger.info("Applying DNS via /etc/resolv.conf")

        try:
            resolv_content = f"""# Generated by SplitWire-Turkey
# Original settings backed up
nameserver {primary}
nameserver {secondary}
"""
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(resolv_content)
                tmp_path = f.name

            # Remove immutable flag if set
            self._run_privileged(["chattr", "-i", "/etc/resolv.conf"])

            result = self._run_privileged(["cp", tmp_path, "/etc/resolv.conf"])
            Path(tmp_path).unlink(missing_ok=True)

            if not result.success:
                self._logger.error(f"Failed to write resolv.conf: {result.stderr}")
                return False

            # Make immutable to prevent overwrites
            self._run_privileged(["chattr", "+i", "/etc/resolv.conf"])

            return True

        except Exception as e:
            self._logger.exception(f"Failed to apply manual DNS: {e}")
            return False

    # =========================================================================
    # Backup and restore methods
    # =========================================================================

    def _backup_current_dns(self) -> bool:
        """Backup current DNS settings."""
        self._logger.info("Backing up current DNS settings")

        try:
            dns_servers = []
            search_domains = []
            doh_enabled = False
            raw_config = None

            if self._dns_manager == DNSManager.SYSTEMD_RESOLVED:
                # Get current DNS from resolvectl
                result = self._shell.run(["resolvectl", "status"], timeout=10)
                if result.success:
                    raw_config = result.stdout

                    # Parse DNS servers
                    for line in result.stdout.split('\n'):
                        if 'DNS Servers:' in line or 'Current DNS Server:' in line:
                            # Extract IP addresses
                            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                            dns_servers.extend(ips)
                        if 'DNS Domain:' in line:
                            domains = line.split(':')[1].strip().split()
                            search_domains.extend(domains)
                        if 'DNSOverTLS' in line and 'yes' in line.lower():
                            doh_enabled = True

            elif self._dns_manager == DNSManager.MANUAL:
                # Read /etc/resolv.conf
                if Path("/etc/resolv.conf").exists():
                    raw_config = Path("/etc/resolv.conf").read_text()
                    for line in raw_config.split('\n'):
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
                        if line.startswith('search'):
                            search_domains.extend(line.split()[1:])

            # Remove duplicates
            dns_servers = list(dict.fromkeys(dns_servers))
            search_domains = list(dict.fromkeys(search_domains))

            backup = DNSBackup(
                timestamp=datetime.now().isoformat(),
                dns_servers=dns_servers,
                search_domains=search_domains,
                doh_enabled=doh_enabled,
                raw_config=raw_config,
            )

            backup_data = {
                "timestamp": backup.timestamp,
                "dns_servers": backup.dns_servers,
                "search_domains": backup.search_domains,
                "doh_enabled": backup.doh_enabled,
                "raw_config": backup.raw_config,
            }
            BACKUP_FILE.write_text(json.dumps(backup_data, indent=2))

            self._config.backup_exists = True
            self._save_config()

            self._logger.info(f"DNS backup saved: {dns_servers}")
            return True

        except Exception as e:
            self._logger.exception(f"Failed to backup DNS: {e}")
            return False

    def _restore_dns(self) -> bool:
        """Restore DNS settings from backup."""
        self._logger.info("Restoring DNS settings from backup")

        if not BACKUP_FILE.exists():
            self._logger.warning("No backup file found")
            return False

        try:
            backup_data = json.loads(BACKUP_FILE.read_text())

            if self._dns_manager == DNSManager.SYSTEMD_RESOLVED:
                # Remove our config file
                self._remove_systemd_resolved()

            elif self._dns_manager == DNSManager.NETWORK_MANAGER:
                # Reset to auto DNS
                result = self._shell.run(
                    ["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"],
                    timeout=10
                )
                if result.success:
                    for conn in result.stdout.strip().split('\n'):
                        if conn:
                            self._run_privileged([
                                "nmcli", "connection", "modify", conn,
                                "ipv4.dns", "",
                                "ipv4.ignore-auto-dns", "no"
                            ])
                    self._run_privileged(["systemctl", "restart", "NetworkManager"])

            elif self._dns_manager == DNSManager.MANUAL:
                # Restore resolv.conf
                dns_servers = backup_data.get("dns_servers", [])
                if dns_servers:
                    self._run_privileged(["chattr", "-i", "/etc/resolv.conf"])

                    content = "# Restored by SplitWire-Turkey\n"
                    for server in dns_servers:
                        content += f"nameserver {server}\n"
                    for domain in backup_data.get("search_domains", []):
                        content += f"search {domain}\n"

                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(content)
                        tmp_path = f.name

                    self._run_privileged(["cp", tmp_path, "/etc/resolv.conf"])
                    Path(tmp_path).unlink(missing_ok=True)

            self._config.enabled = False
            self._save_config()

            self._logger.info("DNS settings restored")
            return True

        except Exception as e:
            self._logger.exception(f"Failed to restore DNS: {e}")
            return False

    def _get_current_dns(self) -> list[str]:
        """Get currently configured DNS servers."""
        dns_servers = []

        try:
            if self._dns_manager == DNSManager.SYSTEMD_RESOLVED:
                result = self._shell.run(["resolvectl", "status"], timeout=10)
                if result.success:
                    for line in result.stdout.split('\n'):
                        if 'DNS Servers:' in line or 'Current DNS Server:' in line:
                            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                            dns_servers.extend(ips)

            elif self._dns_manager == DNSManager.MANUAL:
                if Path("/etc/resolv.conf").exists():
                    content = Path("/etc/resolv.conf").read_text()
                    for line in content.split('\n'):
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])

        except Exception as e:
            self._logger.warning(f"Failed to get current DNS: {e}")

        return list(dict.fromkeys(dns_servers))


# ============================================================================
# Convenience functions
# ============================================================================

_dns_service: Optional[DNSService] = None


def get_dns_service() -> DNSService:
    """Get the global DNS service instance."""
    global _dns_service
    if _dns_service is None:
        _dns_service = DNSService()
    return _dns_service


if __name__ == "__main__":
    # Test the DNS service
    print("=" * 50)
    print("DNS Service Test")
    print("=" * 50)

    service = DNSService()

    print(f"\nService name: {service.name}")
    print(f"Display name: {service.display_name}")
    print(f"Type: {service.service_type.value}")

    print(f"\nDNS Manager: {service.get_dns_manager().value}")
    print(f"Is installed: {service.is_installed()}")
    print(f"Status: {service.status().value}")

    print("\nDNS Presets:")
    for name, preset in DNS_PRESETS.items():
        print(f"  {name}: {preset.name}")
        print(f"    Primary: {preset.primary}")
        print(f"    DoH: {preset.doh_url or 'N/A'}")

    print("\nCurrent DNS servers:")
    for dns in service.get_current_dns():
        print(f"  {dns}")

    config = service.get_config()
    print(f"\nConfig:")
    print(f"  Preset: {config.preset_name}")
    print(f"  DoH Mode: {config.doh_mode.value}")
    print(f"  Auto Apply: {config.auto_apply_on_install}")
    print(f"  Backup Exists: {config.backup_exists}")

    print("\nTest completed!")
