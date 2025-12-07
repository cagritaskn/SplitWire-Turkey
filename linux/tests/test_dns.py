"""
Unit tests for DNS service.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from splitwire.services.dns import (
    DNSService,
    DNSConfig,
    DNSServer,
    DNSBackup,
    DNSManager,
    DoHMode,
    DNS_PRESETS,
    get_dns_service,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestDNSServer:
    """Tests for DNSServer dataclass."""

    def test_dns_server_creation(self):
        """Test creating a DNS server."""
        server = DNSServer(
            name="Test DNS",
            primary="8.8.8.8",
            secondary="8.8.4.4",
            doh_url="https://dns.test/dns-query",
            dot_hostname="dns.test",
        )

        assert server.name == "Test DNS"
        assert server.primary == "8.8.8.8"
        assert server.secondary == "8.8.4.4"
        assert server.doh_url == "https://dns.test/dns-query"
        assert server.dot_hostname == "dns.test"

    def test_dns_server_without_doh(self):
        """Test DNS server without DoH support."""
        server = DNSServer(
            name="Basic DNS",
            primary="1.1.1.1",
            secondary="1.0.0.1",
        )

        assert server.name == "Basic DNS"
        assert server.doh_url is None
        assert server.dot_hostname is None


class TestDNSConfig:
    """Tests for DNSConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DNSConfig()

        assert config.enabled is False
        assert config.preset_name == "cloudflare"
        assert config.custom_primary == ""
        assert config.custom_secondary == ""
        assert config.doh_mode == DoHMode.OPPORTUNISTIC
        assert config.auto_apply_on_install is False
        assert config.backup_exists is False

    def test_config_with_values(self):
        """Test configuration with custom values."""
        config = DNSConfig(
            enabled=True,
            preset_name="google",
            custom_primary="9.9.9.9",
            doh_mode=DoHMode.STRICT,
            auto_apply_on_install=True,
            backup_exists=True,
        )

        assert config.enabled is True
        assert config.preset_name == "google"
        assert config.custom_primary == "9.9.9.9"
        assert config.doh_mode == DoHMode.STRICT
        assert config.auto_apply_on_install is True
        assert config.backup_exists is True


class TestDNSBackup:
    """Tests for DNSBackup dataclass."""

    def test_backup_creation(self):
        """Test creating a DNS backup."""
        backup = DNSBackup(
            timestamp="2024-01-01T00:00:00",
            dns_servers=["8.8.8.8", "8.8.4.4"],
            search_domains=["example.com"],
            doh_enabled=True,
            interface="eth0",
        )

        assert backup.timestamp == "2024-01-01T00:00:00"
        assert backup.dns_servers == ["8.8.8.8", "8.8.4.4"]
        assert backup.search_domains == ["example.com"]
        assert backup.doh_enabled is True
        assert backup.interface == "eth0"


class TestDNSManager:
    """Tests for DNSManager enum."""

    def test_all_managers(self):
        """Test all manager values exist."""
        assert DNSManager.SYSTEMD_RESOLVED.value == "systemd-resolved"
        assert DNSManager.NETWORK_MANAGER.value == "networkmanager"
        assert DNSManager.RESOLVCONF.value == "resolvconf"
        assert DNSManager.MANUAL.value == "manual"
        assert DNSManager.UNKNOWN.value == "unknown"


class TestDoHMode:
    """Tests for DoHMode enum."""

    def test_all_modes(self):
        """Test all DoH mode values exist."""
        assert DoHMode.OFF.value == "off"
        assert DoHMode.OPPORTUNISTIC.value == "opportunistic"
        assert DoHMode.STRICT.value == "strict"


class TestDNSPresets:
    """Tests for DNS presets."""

    def test_presets_exist(self):
        """Test that presets are defined."""
        assert len(DNS_PRESETS) > 0
        assert "google" in DNS_PRESETS
        assert "cloudflare" in DNS_PRESETS
        assert "quad9" in DNS_PRESETS

    def test_google_preset(self):
        """Test Google DNS preset."""
        preset = DNS_PRESETS["google"]

        assert preset.name == "Google DNS"
        assert preset.primary == "8.8.8.8"
        assert preset.secondary == "8.8.4.4"
        assert preset.doh_url == "https://dns.google/dns-query"

    def test_cloudflare_preset(self):
        """Test Cloudflare DNS preset."""
        preset = DNS_PRESETS["cloudflare"]

        assert preset.name == "Cloudflare DNS"
        assert preset.primary == "1.1.1.1"
        assert preset.secondary == "1.0.0.1"
        assert preset.doh_url == "https://cloudflare-dns.com/dns-query"

    def test_quad9_preset(self):
        """Test Quad9 DNS preset."""
        preset = DNS_PRESETS["quad9"]

        assert preset.name == "Quad9 DNS"
        assert preset.primary == "9.9.9.9"
        assert preset.secondary == "149.112.112.112"
        assert "quad9" in preset.doh_url

    def test_all_presets_have_required_fields(self):
        """Test that all presets have required fields."""
        for name, preset in DNS_PRESETS.items():
            assert preset.name, f"Preset {name} missing name"
            assert preset.primary, f"Preset {name} missing primary"
            assert preset.secondary, f"Preset {name} missing secondary"
            # DoH URL is optional (some providers don't support it)

    def test_presets_have_valid_ips(self):
        """Test that presets have valid IP addresses."""
        import re
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

        for name, preset in DNS_PRESETS.items():
            assert ip_pattern.match(preset.primary), f"Invalid primary IP in {name}"
            assert ip_pattern.match(preset.secondary), f"Invalid secondary IP in {name}"


class TestDNSService:
    """Tests for DNSService class."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service with temporary paths."""
        config_dir = tmp_path / "config" / "splitwire" / "dns"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.dns.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.dns.CONFIG_FILE",
            config_dir / "config.json"
        )
        monkeypatch.setattr(
            "splitwire.services.dns.BACKUP_FILE",
            config_dir / "backup.json"
        )

        return DNSService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.name == "dns"
        assert service.display_name == "DNS Service"
        assert service.service_type == ServiceType.DNS

    def test_get_all_presets(self, service):
        """Test getting all presets."""
        presets = service.get_all_presets()

        assert len(presets) >= 3
        assert "google" in presets
        assert "cloudflare" in presets
        assert "quad9" in presets

    def test_get_preset(self, service):
        """Test getting a specific preset."""
        preset = service.get_preset("cloudflare")
        assert preset is not None
        assert preset.name == "Cloudflare DNS"

        # Non-existent preset
        assert service.get_preset("nonexistent") is None

    def test_set_preset(self, service):
        """Test setting active preset."""
        assert service.set_preset("google") is True
        assert service.get_config().preset_name == "google"

        # Invalid preset
        assert service.set_preset("invalid") is False

    def test_set_custom_dns(self, service):
        """Test setting custom DNS servers."""
        service.set_custom_dns("9.9.9.9", "149.112.112.112")

        config = service.get_config()
        assert config.custom_primary == "9.9.9.9"
        assert config.custom_secondary == "149.112.112.112"

    def test_set_doh_mode(self, service):
        """Test setting DoH mode."""
        service.set_doh_mode(DoHMode.STRICT)
        assert service.get_config().doh_mode == DoHMode.STRICT

        service.set_doh_mode(DoHMode.OFF)
        assert service.get_config().doh_mode == DoHMode.OFF

    def test_set_auto_apply(self, service):
        """Test setting auto-apply option."""
        assert service.get_config().auto_apply_on_install is False

        service.set_auto_apply(True)
        assert service.get_config().auto_apply_on_install is True

    def test_should_auto_apply(self, service):
        """Test should_auto_apply method."""
        assert service.should_auto_apply() is False

        service.set_auto_apply(True)
        assert service.should_auto_apply() is True

    def test_has_backup_false(self, service):
        """Test has_backup returns false when no backup."""
        assert service.has_backup() is False

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        status = service.status()
        assert status == ServiceStatus.NOT_INSTALLED

    def test_is_installed_false(self, service):
        """Test is_installed returns false when not installed."""
        assert service.is_installed() is False


class TestDNSServiceConfig:
    """Tests for DNS service configuration persistence."""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create temporary config directory."""
        config_dir = tmp_path / "config" / "splitwire" / "dns"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @pytest.fixture
    def service(self, config_dir, monkeypatch):
        """Create service with temporary paths."""
        config_file = config_dir / "config.json"
        backup_file = config_dir / "backup.json"

        monkeypatch.setattr(
            "splitwire.services.dns.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.dns.CONFIG_FILE",
            config_file
        )
        monkeypatch.setattr(
            "splitwire.services.dns.BACKUP_FILE",
            backup_file
        )

        return DNSService()

    def test_save_and_load_config(self, service, config_dir):
        """Test saving and loading configuration."""
        # Modify config
        service._config.enabled = True
        service._config.preset_name = "quad9"
        service._config.doh_mode = DoHMode.STRICT
        service._config.auto_apply_on_install = True
        service._save_config()

        # Verify file exists
        config_file = config_dir / "config.json"
        assert config_file.exists()

        # Create new service to load config
        new_service = DNSService()
        config = new_service.get_config()

        assert config.enabled is True
        assert config.preset_name == "quad9"
        assert config.doh_mode == DoHMode.STRICT
        assert config.auto_apply_on_install is True


class TestDNSManagerDetection:
    """Tests for DNS manager detection."""

    @pytest.fixture
    def service(self, tmp_path, monkeypatch):
        """Create a test service."""
        config_dir = tmp_path / "config" / "splitwire" / "dns"
        config_dir.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(
            "splitwire.services.dns.LOCAL_CONFIG_DIR",
            config_dir
        )
        monkeypatch.setattr(
            "splitwire.services.dns.CONFIG_FILE",
            config_dir / "config.json"
        )
        monkeypatch.setattr(
            "splitwire.services.dns.BACKUP_FILE",
            config_dir / "backup.json"
        )

        return DNSService()

    def test_get_dns_manager(self, service):
        """Test getting DNS manager."""
        manager = service.get_dns_manager()
        # Should return a valid DNSManager enum value
        assert isinstance(manager, DNSManager)


class TestDNSPresetDetails:
    """Tests for specific DNS preset details."""

    def test_cloudflare_family_preset(self):
        """Test Cloudflare Family DNS preset."""
        preset = DNS_PRESETS.get("cloudflare_family")
        assert preset is not None
        assert preset.primary == "1.1.1.3"
        assert "family" in preset.doh_url.lower()

    def test_opendns_preset(self):
        """Test OpenDNS preset."""
        preset = DNS_PRESETS.get("opendns")
        assert preset is not None
        assert preset.name == "OpenDNS"
        assert preset.doh_url is not None

    def test_adguard_preset(self):
        """Test AdGuard DNS preset."""
        preset = DNS_PRESETS.get("adguard")
        assert preset is not None
        assert "adguard" in preset.doh_url.lower()

    def test_turkish_telecom_preset(self):
        """Test Turkish Telecom DNS preset (no DoH)."""
        preset = DNS_PRESETS.get("turkish_telecom")
        assert preset is not None
        assert preset.doh_url is None  # No DoH support
        assert preset.primary == "195.175.39.39"


class TestGetDNSService:
    """Tests for get_dns_service function."""

    def test_returns_service(self):
        """Test that function returns a service."""
        # Reset singleton
        import splitwire.services.dns as module
        module._dns_service = None

        service = get_dns_service()
        assert isinstance(service, DNSService)


class TestDoHModeStrings:
    """Tests for DoH mode string conversion."""

    def test_doh_mode_values(self):
        """Test DoH mode enum values for systemd-resolved."""
        # These values are used in resolved.conf
        assert DoHMode.OFF.value == "off"
        assert DoHMode.OPPORTUNISTIC.value == "opportunistic"
        assert DoHMode.STRICT.value == "strict"

    def test_doh_mode_from_string(self):
        """Test creating DoH mode from string."""
        assert DoHMode("off") == DoHMode.OFF
        assert DoHMode("opportunistic") == DoHMode.OPPORTUNISTIC
        assert DoHMode("strict") == DoHMode.STRICT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
