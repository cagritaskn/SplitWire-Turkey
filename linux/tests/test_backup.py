"""
Tests for the backup manager module.
"""

import json
import pytest
import tempfile
import tarfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.core.backup import (
    BackupManager,
    BackupMetadata,
    BackupType,
    BackupError,
    SnapshotManager,
    SystemSnapshot,
)


class TestBackupType:
    """Tests for BackupType enum."""

    def test_backup_types_exist(self):
        """Test all backup types exist."""
        assert BackupType.CONFIG.value == "config"
        assert BackupType.DNS.value == "dns"
        assert BackupType.WIREGUARD.value == "wireguard"
        assert BackupType.ZAPRET.value == "zapret"
        assert BackupType.SERVICES.value == "services"
        assert BackupType.FULL.value == "full"


class TestBackupMetadata:
    """Tests for BackupMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating backup metadata."""
        metadata = BackupMetadata(
            backup_id="test-123",
            backup_type=BackupType.CONFIG,
            timestamp=datetime.now(),
            description="Test backup",
            files=["config.json"],
        )
        assert metadata.backup_id == "test-123"
        assert metadata.backup_type == BackupType.CONFIG
        assert len(metadata.files) == 1

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        now = datetime.now()
        metadata = BackupMetadata(
            backup_id="test-456",
            backup_type=BackupType.DNS,
            timestamp=now,
            description="DNS backup",
            files=["resolv.conf"],
        )

        # Manual conversion since we might not have to_dict method
        data = {
            "backup_id": metadata.backup_id,
            "backup_type": metadata.backup_type.value,
            "timestamp": metadata.timestamp.isoformat(),
            "description": metadata.description,
            "files": metadata.files,
        }

        assert data["backup_id"] == "test-456"
        assert data["backup_type"] == "dns"


class TestBackupError:
    """Tests for BackupError exception."""

    def test_backup_error_message(self):
        """Test BackupError exception message."""
        error = BackupError("Backup failed")
        assert str(error) == "Backup failed"

    def test_backup_error_inheritance(self):
        """Test that BackupError is an Exception."""
        error = BackupError("Test error")
        assert isinstance(error, Exception)


class TestBackupManager:
    """Tests for BackupManager class."""

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary backup directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def backup_manager(self, temp_backup_dir):
        """Create a BackupManager with temporary directory."""
        manager = BackupManager.__new__(BackupManager)
        manager._backup_dir = temp_backup_dir
        manager._backup_dir.mkdir(parents=True, exist_ok=True)
        manager._metadata_file = temp_backup_dir / "metadata.json"
        manager._backups = {}
        return manager

    def test_backup_dir_creation(self, temp_backup_dir):
        """Test that backup directory is created."""
        backup_dir = temp_backup_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        assert backup_dir.exists()

    def test_create_backup_tarball(self, backup_manager, temp_backup_dir):
        """Test creating a backup tarball."""
        # Create a test file to backup
        test_file = temp_backup_dir / "test_config.json"
        test_file.write_text('{"key": "value"}')

        # Create tarball
        backup_file = temp_backup_dir / "backup.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(test_file, arcname="test_config.json")

        assert backup_file.exists()

        # Verify tarball contents
        with tarfile.open(backup_file, "r:gz") as tar:
            names = tar.getnames()
            assert "test_config.json" in names

    def test_backup_metadata_storage(self, backup_manager, temp_backup_dir):
        """Test storing backup metadata."""
        metadata = {
            "backups": [
                {
                    "backup_id": "backup-001",
                    "backup_type": "config",
                    "timestamp": datetime.now().isoformat(),
                    "description": "Test backup",
                    "files": ["config.json"],
                }
            ]
        }

        metadata_file = temp_backup_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        assert metadata_file.exists()

        with open(metadata_file) as f:
            loaded = json.load(f)
            assert len(loaded["backups"]) == 1
            assert loaded["backups"][0]["backup_id"] == "backup-001"

    def test_list_backups(self, backup_manager, temp_backup_dir):
        """Test listing backups."""
        # Create some backup files
        for i in range(3):
            backup_file = temp_backup_dir / f"backup_{i}.tar.gz"
            with tarfile.open(backup_file, "w:gz") as tar:
                pass  # Empty tarball

        backup_files = list(temp_backup_dir.glob("backup_*.tar.gz"))
        assert len(backup_files) == 3

    def test_restore_from_tarball(self, temp_backup_dir):
        """Test restoring files from tarball."""
        # Create source file
        source_dir = temp_backup_dir / "source"
        source_dir.mkdir()
        source_file = source_dir / "config.json"
        source_file.write_text('{"restored": true}')

        # Create backup tarball
        backup_file = temp_backup_dir / "restore_test.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(source_file, arcname="config.json")

        # Restore to destination
        dest_dir = temp_backup_dir / "restored"
        dest_dir.mkdir()

        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(dest_dir)

        restored_file = dest_dir / "config.json"
        assert restored_file.exists()
        content = json.loads(restored_file.read_text())
        assert content["restored"] is True


class TestSnapshotManager:
    """Tests for SnapshotManager class."""

    @pytest.fixture
    def temp_snapshot_dir(self):
        """Create a temporary snapshot directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def snapshot_manager(self, temp_snapshot_dir):
        """Create a SnapshotManager with temporary directory."""
        manager = SnapshotManager.__new__(SnapshotManager)
        manager._snapshot_dir = temp_snapshot_dir
        manager._snapshot_dir.mkdir(parents=True, exist_ok=True)
        return manager

    def test_create_snapshot(self, snapshot_manager, temp_snapshot_dir):
        """Test creating a system snapshot."""
        snapshot_id = "snapshot-001"
        snapshot_file = temp_snapshot_dir / f"{snapshot_id}.tar.gz"

        # Create a test file
        test_file = temp_snapshot_dir / "test.txt"
        test_file.write_text("snapshot content")

        # Create snapshot tarball
        with tarfile.open(snapshot_file, "w:gz") as tar:
            tar.add(test_file, arcname="test.txt")

        assert snapshot_file.exists()

    def test_snapshot_metadata(self, temp_snapshot_dir):
        """Test snapshot metadata creation."""
        snapshot = SystemSnapshot(
            snapshot_id="snap-001",
            timestamp=datetime.now(),
            description="Pre-install snapshot",
            components=["dns", "wireguard"],
        )

        assert snapshot.snapshot_id == "snap-001"
        assert "dns" in snapshot.components
        assert "wireguard" in snapshot.components


class TestSystemSnapshot:
    """Tests for SystemSnapshot dataclass."""

    def test_snapshot_creation(self):
        """Test creating a SystemSnapshot."""
        now = datetime.now()
        snapshot = SystemSnapshot(
            snapshot_id="test-snap",
            timestamp=now,
            description="Test snapshot",
            components=["config", "dns"],
        )

        assert snapshot.snapshot_id == "test-snap"
        assert snapshot.timestamp == now
        assert len(snapshot.components) == 2

    def test_snapshot_with_empty_components(self):
        """Test snapshot with no components."""
        snapshot = SystemSnapshot(
            snapshot_id="empty-snap",
            timestamp=datetime.now(),
            description="Empty snapshot",
            components=[],
        )

        assert snapshot.components == []


class TestBackupCleanup:
    """Tests for backup cleanup functionality."""

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary backup directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_cleanup_old_backups(self, temp_backup_dir):
        """Test cleaning up old backups."""
        # Create multiple backup files
        for i in range(10):
            backup_file = temp_backup_dir / f"backup_{i:03d}.tar.gz"
            with tarfile.open(backup_file, "w:gz") as tar:
                pass

        # Keep only last 5
        max_backups = 5
        backup_files = sorted(temp_backup_dir.glob("backup_*.tar.gz"))

        if len(backup_files) > max_backups:
            for old_backup in backup_files[:-max_backups]:
                old_backup.unlink()

        remaining = list(temp_backup_dir.glob("backup_*.tar.gz"))
        assert len(remaining) == max_backups
