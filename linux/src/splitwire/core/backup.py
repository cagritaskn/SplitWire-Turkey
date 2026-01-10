"""
Backup and rollback system for SplitWire-Turkey Linux.

Provides:
- Configuration backup and restore
- System state snapshots before changes
- Rollback capability for failed operations
"""

import json
import shutil
import tarfile
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Any
import hashlib


class BackupType(Enum):
    """Type of backup."""
    CONFIG = "config"           # Application configuration
    DNS = "dns"                 # DNS settings
    WIREGUARD = "wireguard"     # WireGuard configs
    ZAPRET = "zapret"           # Zapret settings
    SERVICES = "services"       # Service states
    FULL = "full"               # Everything


@dataclass
class BackupMetadata:
    """Metadata for a backup."""
    id: str
    type: BackupType
    timestamp: str
    description: str
    version: str
    files: list[str]
    size: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "description": self.description,
            "version": self.version,
            "files": self.files,
            "size": self.size
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackupMetadata":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=BackupType(data["type"]),
            timestamp=data["timestamp"],
            description=data["description"],
            version=data["version"],
            files=data.get("files", []),
            size=data.get("size", 0)
        )


class BackupError(Exception):
    """Exception raised for backup-related errors."""
    pass


class BackupManager:
    """
    Manages backups and rollback operations.

    Backups are stored in ~/.local/share/splitwire/backups/
    """

    APP_VERSION = "1.0.0"
    MAX_BACKUPS = 10  # Maximum number of backups to keep
    METADATA_FILE = "backup_metadata.json"

    def __init__(self, backup_dir: Optional[Path] = None, config_dir: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            backup_dir: Override backup directory
            config_dir: Override config directory (for determining what to backup)
        """
        # Determine directories
        if backup_dir:
            self._backup_dir = backup_dir
        else:
            xdg_data = Path.home() / ".local" / "share" / "splitwire"
            self._backup_dir = xdg_data / "backups"

        if config_dir:
            self._config_dir = config_dir
        else:
            xdg_config = Path.home() / ".config" / "splitwire"
            self._config_dir = xdg_config

        # Data directory (WireGuard configs, Zapret, etc.)
        self._data_dir = Path.home() / ".local" / "share" / "splitwire"

        # Ensure directories exist
        self._backup_dir.mkdir(parents=True, exist_ok=True)

    @property
    def backup_dir(self) -> Path:
        """Get backup directory path."""
        return self._backup_dir

    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{timestamp}_{id(self)}".encode()
        short_hash = hashlib.md5(hash_input).hexdigest()[:8]
        return f"{timestamp}_{short_hash}"

    def _get_backup_path(self, backup_id: str) -> Path:
        """Get path for a backup."""
        return self._backup_dir / f"{backup_id}.tar.gz"

    def _get_metadata_path(self, backup_id: str) -> Path:
        """Get path for backup metadata."""
        return self._backup_dir / f"{backup_id}.json"

    def create_backup(
        self,
        backup_type: BackupType = BackupType.CONFIG,
        description: str = ""
    ) -> BackupMetadata:
        """
        Create a new backup.

        Args:
            backup_type: Type of backup to create
            description: Human-readable description

        Returns:
            Backup metadata

        Raises:
            BackupError: If backup fails
        """
        backup_id = self._generate_backup_id()
        backup_path = self._get_backup_path(backup_id)
        timestamp = datetime.now().isoformat()

        # Determine files to backup
        files_to_backup = self._get_files_for_backup(backup_type)

        if not files_to_backup:
            raise BackupError(f"No files found for backup type: {backup_type.value}")

        # Create tarball
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in files_to_backup:
                    path = Path(file_path)
                    if path.exists():
                        # Use relative path within backup
                        # Use unique marker to avoid collisions with real paths
                        home_str = str(Path.home())
                        path_str = str(path)
                        if path_str.startswith(home_str):
                            arcname = "__USER_HOME__" + path_str[len(home_str):]
                        else:
                            arcname = path_str
                        tar.add(str(path), arcname=arcname)
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Failed to create backup archive: {e}")

        # Get backup size
        backup_size = backup_path.stat().st_size

        # Create metadata
        metadata = BackupMetadata(
            id=backup_id,
            type=backup_type,
            timestamp=timestamp,
            description=description or f"{backup_type.value} backup",
            version=self.APP_VERSION,
            files=[str(f) for f in files_to_backup],
            size=backup_size
        )

        # Save metadata
        metadata_path = self._get_metadata_path(backup_id)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        # Cleanup old backups
        self._cleanup_old_backups()

        return metadata

    def _get_files_for_backup(self, backup_type: BackupType) -> list[Path]:
        """Get list of files to backup for a given type."""
        files = []

        if backup_type in (BackupType.CONFIG, BackupType.FULL):
            # Application config
            config_file = self._config_dir / "config.json"
            if config_file.exists():
                files.append(config_file)

        if backup_type in (BackupType.DNS, BackupType.FULL):
            # DNS backup (resolv.conf if we modified it)
            resolv_backup = self._data_dir / "dns_backup"
            if resolv_backup.exists():
                files.append(resolv_backup)

        if backup_type in (BackupType.WIREGUARD, BackupType.FULL):
            # WireGuard configs
            wg_dir = self._data_dir / "wireguard"
            if wg_dir.exists():
                for conf in wg_dir.glob("*.conf"):
                    files.append(conf)

        if backup_type in (BackupType.ZAPRET, BackupType.FULL):
            # Zapret configs
            zapret_dir = self._data_dir / "zapret"
            if zapret_dir.exists():
                # Only backup config files, not binaries
                for pattern in ["*.conf", "*.config", "*.txt", "*.sh"]:
                    for f in zapret_dir.glob(f"**/{pattern}"):
                        files.append(f)

        if backup_type == BackupType.SERVICES:
            # Service state files
            services_file = self._data_dir / "services_state.json"
            if services_file.exists():
                files.append(services_file)

        return files

    def restore_backup(self, backup_id: str, dry_run: bool = False) -> list[str]:
        """
        Restore a backup.

        Args:
            backup_id: ID of backup to restore
            dry_run: If True, only list files that would be restored

        Returns:
            List of restored file paths

        Raises:
            BackupError: If restore fails
        """
        backup_path = self._get_backup_path(backup_id)
        metadata_path = self._get_metadata_path(backup_id)

        if not backup_path.exists():
            raise BackupError(f"Backup not found: {backup_id}")

        # Load metadata
        metadata = self.get_backup_metadata(backup_id)
        if metadata is None:
            raise BackupError(f"Backup metadata not found: {backup_id}")

        restored_files = []

        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                for member in tar.getmembers():
                    # Convert archive path back to real path
                    # Handle both old "HOME" marker and new "__USER_HOME__" marker
                    if member.name.startswith("__USER_HOME__"):
                        real_path = str(Path.home()) + member.name[len("__USER_HOME__"):]
                    elif member.name.startswith("HOME"):
                        # Legacy support for old backups
                        real_path = str(Path.home()) + member.name[4:]
                    else:
                        real_path = member.name
                    restored_files.append(real_path)

                    if not dry_run:
                        # Ensure parent directory exists
                        Path(real_path).parent.mkdir(parents=True, exist_ok=True)

                        # Extract file
                        member.name = real_path
                        tar.extract(member, path="/")

        except Exception as e:
            raise BackupError(f"Failed to restore backup: {e}")

        return restored_files

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: ID of backup to delete

        Returns:
            True if deleted successfully
        """
        backup_path = self._get_backup_path(backup_id)
        metadata_path = self._get_metadata_path(backup_id)

        deleted = False

        if backup_path.exists():
            backup_path.unlink()
            deleted = True

        if metadata_path.exists():
            metadata_path.unlink()
            deleted = True

        return deleted

    def list_backups(self, backup_type: Optional[BackupType] = None) -> list[BackupMetadata]:
        """
        List all backups.

        Args:
            backup_type: Filter by type (optional)

        Returns:
            List of backup metadata, sorted by timestamp (newest first)
        """
        backups = []

        for metadata_file in self._backup_dir.glob("*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = BackupMetadata.from_dict(data)

                    if backup_type is None or metadata.type == backup_type:
                        backups.append(metadata)
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)

        return backups

    def get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """
        Get metadata for a specific backup.

        Args:
            backup_id: Backup ID

        Returns:
            Backup metadata or None if not found
        """
        metadata_path = self._get_metadata_path(backup_id)

        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return BackupMetadata.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def get_latest_backup(self, backup_type: Optional[BackupType] = None) -> Optional[BackupMetadata]:
        """
        Get the most recent backup.

        Args:
            backup_type: Filter by type (optional)

        Returns:
            Latest backup metadata or None
        """
        backups = self.list_backups(backup_type)
        return backups[0] if backups else None

    def _cleanup_old_backups(self) -> int:
        """
        Remove old backups exceeding MAX_BACKUPS.

        Returns:
            Number of backups removed
        """
        backups = self.list_backups()

        if len(backups) <= self.MAX_BACKUPS:
            return 0

        # Remove oldest backups
        removed = 0
        for backup in backups[self.MAX_BACKUPS:]:
            if self.delete_backup(backup.id):
                removed += 1

        return removed

    def get_total_backup_size(self) -> int:
        """
        Get total size of all backups in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for backup_file in self._backup_dir.glob("*.tar.gz"):
            total += backup_file.stat().st_size
        return total


# Snapshot system for atomic operations

@dataclass
class SystemSnapshot:
    """Snapshot of system state before an operation."""
    id: str
    timestamp: str
    operation: str
    files_backed_up: list[str]
    services_state: dict[str, str]
    dns_state: Optional[str] = None


class SnapshotManager:
    """
    Manages system snapshots for rollback capability.

    Used to capture state before potentially destructive operations.
    """

    def __init__(self, snapshot_dir: Optional[Path] = None):
        """
        Initialize snapshot manager.

        Args:
            snapshot_dir: Override snapshot directory
        """
        if snapshot_dir:
            self._snapshot_dir = snapshot_dir
        else:
            xdg_cache = Path.home() / ".cache" / "splitwire"
            self._snapshot_dir = xdg_cache / "snapshots"

        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._current_snapshot: Optional[SystemSnapshot] = None

    def create_snapshot(self, operation: str, files: list[str]) -> SystemSnapshot:
        """
        Create a snapshot before an operation.

        Args:
            operation: Description of operation being performed
            files: Files that may be modified

        Returns:
            Created snapshot
        """
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        snapshot_path = self._snapshot_dir / snapshot_id

        # Create snapshot directory
        snapshot_path.mkdir(parents=True, exist_ok=True)

        # Backup files
        backed_up = []
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                dest = snapshot_path / path.name
                shutil.copy2(str(path), str(dest))
                backed_up.append(file_path)

        # Capture service states
        services_state = self._capture_services_state()

        # Capture DNS state
        dns_state = self._capture_dns_state()

        snapshot = SystemSnapshot(
            id=snapshot_id,
            timestamp=datetime.now().isoformat(),
            operation=operation,
            files_backed_up=backed_up,
            services_state=services_state,
            dns_state=dns_state
        )

        # Save snapshot metadata
        meta_path = snapshot_path / "snapshot.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(asdict(snapshot), f, indent=2)

        self._current_snapshot = snapshot
        return snapshot

    def rollback(self, snapshot_id: Optional[str] = None) -> bool:
        """
        Rollback to a snapshot.

        Args:
            snapshot_id: ID of snapshot to rollback to (default: current)

        Returns:
            True if rollback succeeded
        """
        if snapshot_id is None and self._current_snapshot is not None:
            snapshot_id = self._current_snapshot.id

        if snapshot_id is None:
            return False

        snapshot_path = self._snapshot_dir / snapshot_id

        if not snapshot_path.exists():
            return False

        # Load snapshot metadata
        meta_path = snapshot_path / "snapshot.json"
        if not meta_path.exists():
            return False

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                snapshot_data = json.load(f)

            # Restore backed up files
            for original_path in snapshot_data["files_backed_up"]:
                original = Path(original_path)
                backup = snapshot_path / original.name

                if backup.exists():
                    shutil.copy2(str(backup), str(original))

            return True

        except Exception:
            return False

    def cleanup_snapshot(self, snapshot_id: Optional[str] = None) -> bool:
        """
        Remove a snapshot after successful operation.

        Args:
            snapshot_id: ID of snapshot to cleanup (default: current)

        Returns:
            True if cleanup succeeded
        """
        if snapshot_id is None and self._current_snapshot is not None:
            snapshot_id = self._current_snapshot.id
            self._current_snapshot = None

        if snapshot_id is None:
            return False

        snapshot_path = self._snapshot_dir / snapshot_id

        if snapshot_path.exists():
            shutil.rmtree(snapshot_path)
            return True

        return False

    def _capture_services_state(self) -> dict[str, str]:
        """Capture current service states."""
        import subprocess

        services = ["wg-quick@splitwire", "zapret", "ciadpi"]
        states = {}

        for service in services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                states[service] = result.stdout.strip()
            except Exception:
                states[service] = "unknown"

        return states

    def _capture_dns_state(self) -> Optional[str]:
        """Capture current DNS configuration."""
        resolv_conf = Path("/etc/resolv.conf")

        if resolv_conf.exists():
            try:
                return resolv_conf.read_text()
            except IOError:
                pass

        return None


# Global instances
_backup_manager: Optional[BackupManager] = None
_snapshot_manager: Optional[SnapshotManager] = None


def get_backup_manager() -> BackupManager:
    """Get the global BackupManager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager


def get_snapshot_manager() -> SnapshotManager:
    """Get the global SnapshotManager instance."""
    global _snapshot_manager
    if _snapshot_manager is None:
        _snapshot_manager = SnapshotManager()
    return _snapshot_manager


# Convenience functions
def create_backup(backup_type: BackupType = BackupType.CONFIG, description: str = "") -> BackupMetadata:
    """Create a backup (convenience function)."""
    return get_backup_manager().create_backup(backup_type, description)


def restore_backup(backup_id: str) -> list[str]:
    """Restore a backup (convenience function)."""
    return get_backup_manager().restore_backup(backup_id)


def list_backups(backup_type: Optional[BackupType] = None) -> list[BackupMetadata]:
    """List backups (convenience function)."""
    return get_backup_manager().list_backups(backup_type)


if __name__ == "__main__":
    # Test the backup system
    import tempfile

    print("=" * 50)
    print("Backup System Test")
    print("=" * 50)

    # Create test directories
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir) / "backups"
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir(parents=True)

        # Create test config file
        test_config = config_dir / "config.json"
        test_config.write_text('{"theme": "dark", "language": "en"}')

        # Initialize manager with test paths
        manager = BackupManager(backup_dir=backup_dir, config_dir=config_dir)
        manager._data_dir = config_dir  # Use config dir as data dir for test

        print(f"\nBackup directory: {manager.backup_dir}")

        # Create backup
        print("\n--- Creating backup ---")
        try:
            metadata = manager.create_backup(
                BackupType.CONFIG,
                "Test backup before changes"
            )
            print(f"Backup created: {metadata.id}")
            print(f"Type: {metadata.type.value}")
            print(f"Files: {metadata.files}")
            print(f"Size: {metadata.size} bytes")
        except BackupError as e:
            print(f"Backup failed: {e}")

        # List backups
        print("\n--- Listing backups ---")
        backups = manager.list_backups()
        for b in backups:
            print(f"  {b.id}: {b.description} ({b.type.value})")

        # Modify config
        print("\n--- Modifying config ---")
        test_config.write_text('{"theme": "light", "language": "tr"}')
        print(f"New config: {test_config.read_text()}")

        # Restore backup
        if backups:
            print("\n--- Restoring backup ---")
            restored = manager.restore_backup(backups[0].id)
            print(f"Restored files: {restored}")
            print(f"Restored config: {test_config.read_text()}")

        # Test snapshot manager
        print("\n--- Snapshot Test ---")
        snapshot_dir = Path(tmpdir) / "snapshots"
        snap_manager = SnapshotManager(snapshot_dir)

        # Create snapshot
        snapshot = snap_manager.create_snapshot(
            "test_operation",
            [str(test_config)]
        )
        print(f"Snapshot created: {snapshot.id}")

        # Modify file
        test_config.write_text('{"modified": true}')
        print(f"Modified: {test_config.read_text()}")

        # Rollback
        if snap_manager.rollback():
            print(f"Rolled back: {test_config.read_text()}")

        # Cleanup
        snap_manager.cleanup_snapshot()
        print("Snapshot cleaned up")

    print("\nTest completed!")
