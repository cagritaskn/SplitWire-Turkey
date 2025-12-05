"""
Tests for the WireGuard service module.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.wireguard import (
    WireGuardService,
    WireGuardInterface,
    WGCFAccount,
    get_wireguard_service,
    WIREGUARD_CONFIG_DIR,
    SPLITWIRE_CONFIG_FILE,
    DEFAULT_EXCLUDED_NETWORKS,
)
from splitwire.services.base import ServiceStatus, ServiceType


class TestWireGuardInterface:
    """Tests for WireGuardInterface dataclass."""

    def test_basic_creation(self):
        """Test creating WireGuardInterface."""
        interface = WireGuardInterface(name="wg0")
        assert interface.name == "wg0"
        assert interface.public_key == ""
        assert interface.allowed_ips == []

    def test_full_creation(self):
        """Test creating WireGuardInterface with all fields."""
        interface = WireGuardInterface(
            name="splitwire",
            public_key="ABC123...",
            private_key="XYZ789...",
            address="10.0.0.2/32",
            listen_port=51820,
            endpoint="engage.cloudflareclient.com:2408",
            latest_handshake="2 minutes ago",
            transfer_rx=1024 * 1024,
            transfer_tx=512 * 1024,
            allowed_ips=["0.0.0.0/0", "::/0"],
        )
        assert interface.endpoint == "engage.cloudflareclient.com:2408"
        assert len(interface.allowed_ips) == 2
        assert interface.transfer_rx == 1024 * 1024


class TestWGCFAccount:
    """Tests for WGCFAccount dataclass."""

    def test_creation(self):
        """Test creating WGCFAccount."""
        account = WGCFAccount(
            device_id="abc123",
            access_token="token456",
            private_key="privatekey",
            license_key="",
            created="2024-01-01",
        )
        assert account.device_id == "abc123"
        assert account.access_token == "token456"


class TestWireGuardService:
    """Tests for WireGuardService class."""

    @pytest.fixture
    def service(self):
        """Create a WireGuard service instance."""
        with patch('splitwire.services.wireguard.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.wireguard.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                service = WireGuardService()
                return service

    def test_service_properties(self, service):
        """Test service properties."""
        assert service.name == "wireguard"
        assert service.display_name == "WireGuard VPN"
        assert service.service_type == ServiceType.VPN

    def test_not_installed_initially(self, service):
        """Test service is not installed by default."""
        with patch.object(Path, 'exists', return_value=False):
            assert not service.is_installed()

    def test_status_not_installed(self, service):
        """Test status when not installed."""
        with patch.object(service, 'is_installed', return_value=False):
            assert service.status() == ServiceStatus.NOT_INSTALLED

    def test_status_running(self, service):
        """Test status when running."""
        with patch.object(service, 'is_installed', return_value=True):
            service._shell.run.return_value = MagicMock(success=True)
            assert service.status() == ServiceStatus.RUNNING

    def test_status_stopped(self, service):
        """Test status when stopped."""
        with patch.object(service, 'is_installed', return_value=True):
            service._shell.run.return_value = MagicMock(success=False)
            assert service.status() == ServiceStatus.STOPPED

    def test_check_dependencies(self, service):
        """Test dependency checking."""
        # Mock all commands exist
        service._shell.command_exists.return_value = True
        assert service._check_dependencies()

        # Mock wg missing
        service._shell.command_exists.side_effect = lambda cmd: cmd != "wg"
        assert not service._check_dependencies()

    def test_modify_allowed_ips(self, service):
        """Test AllowedIPs modification."""
        original = """[Interface]
PrivateKey = abc123
Address = 10.0.0.2/32

[Peer]
PublicKey = xyz789
AllowedIPs = 0.0.0.0/0
Endpoint = example.com:51820
"""
        modified = service._modify_allowed_ips(original)
        assert "AllowedIPs" in modified
        assert "0.0.0.0/0" in modified

    def test_add_dns_config(self, service):
        """Test adding DNS configuration."""
        original = """[Interface]
PrivateKey = abc123
Address = 10.0.0.2/32

[Peer]
PublicKey = xyz789
"""
        modified = service._add_dns_config(original)
        assert "DNS = 1.1.1.1" in modified

    def test_add_dns_config_already_present(self, service):
        """Test DNS not duplicated if already present."""
        original = """[Interface]
PrivateKey = abc123
Address = 10.0.0.2/32
DNS = 8.8.8.8

[Peer]
PublicKey = xyz789
"""
        modified = service._add_dns_config(original)
        # Should not add another DNS line
        assert modified.count("DNS =") == 1

    def test_parse_wg_show(self, service):
        """Test parsing wg show output."""
        output = """interface: splitwire
  public key: abcdef123456
  private key: (hidden)
  listening port: 51820

peer: xyz789abc
  endpoint: 1.2.3.4:51820
  allowed ips: 0.0.0.0/0, ::/0
  latest handshake: 1 minute, 30 seconds ago
  transfer: 1.5 MiB received, 0.8 MiB sent
"""
        interface = service._parse_wg_show(output)
        assert interface.name == "splitwire"
        assert "abcdef123456" in interface.public_key
        assert interface.listen_port == 51820


class TestWireGuardServiceIntegration:
    """Integration tests for WireGuard service."""

    @pytest.fixture
    def temp_wgcf_dir(self):
        """Create temporary WGCF directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_get_wireguard_service_singleton(self):
        """Test that get_wireguard_service returns singleton."""
        # Reset the global
        import splitwire.services.wireguard as wg_module
        wg_module._wireguard_service = None

        service1 = get_wireguard_service()
        service2 = get_wireguard_service()
        assert service1 is service2


class TestDefaultExcludedNetworks:
    """Tests for default excluded networks constant."""

    def test_excluded_networks_format(self):
        """Test excluded networks are valid CIDR format."""
        import ipaddress

        for network in DEFAULT_EXCLUDED_NETWORKS:
            # Should not raise an exception
            ipaddress.ip_network(network)

    def test_private_networks_included(self):
        """Test common private networks are excluded."""
        assert "10.0.0.0/8" in DEFAULT_EXCLUDED_NETWORKS
        assert "172.16.0.0/12" in DEFAULT_EXCLUDED_NETWORKS
        assert "192.168.0.0/16" in DEFAULT_EXCLUDED_NETWORKS
        assert "127.0.0.0/8" in DEFAULT_EXCLUDED_NETWORKS
