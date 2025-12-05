"""
Core modules for SplitWire-Turkey Linux.

This package contains:
- config: Configuration management (XDG paths, JSON storage)
- language: Localization and translation
- logger: Logging system
- shell: Shell command execution
- backup: Backup and rollback system
"""

from .config import (
    ConfigManager,
    AppConfig,
    DNSConfig,
    WireGuardConfig,
    ZapretConfig,
    ByeDPIConfig,
    Theme,
    Language,
    get_config_manager,
    get_config,
    save_config,
)

from .language import (
    LanguageManager,
    LanguageError,
    get_language_manager,
    init_language_manager,
    get_text,
    format_text,
    set_language,
    get_current_language,
)

from .logger import (
    SplitWireLogger,
    ColoredFormatter,
    get_logger,
    init_logger,
    get_component_logger,
    debug,
    info,
    warning,
    error,
    critical,
    exception,
)

from .shell import (
    ShellExecutor,
    CommandResult,
    CommandStatus,
    get_shell,
    run,
    run_async,
    command_exists,
)

from .backup import (
    BackupManager,
    BackupMetadata,
    BackupType,
    BackupError,
    SnapshotManager,
    SystemSnapshot,
    get_backup_manager,
    get_snapshot_manager,
    create_backup,
    restore_backup,
    list_backups,
)

__all__ = [
    # config
    "ConfigManager",
    "AppConfig",
    "DNSConfig",
    "WireGuardConfig",
    "ZapretConfig",
    "ByeDPIConfig",
    "Theme",
    "Language",
    "get_config_manager",
    "get_config",
    "save_config",
    # language
    "LanguageManager",
    "LanguageError",
    "get_language_manager",
    "init_language_manager",
    "get_text",
    "format_text",
    "set_language",
    "get_current_language",
    # logger
    "SplitWireLogger",
    "ColoredFormatter",
    "get_logger",
    "init_logger",
    "get_component_logger",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    # shell
    "ShellExecutor",
    "CommandResult",
    "CommandStatus",
    "get_shell",
    "run",
    "run_async",
    "command_exists",
    # backup
    "BackupManager",
    "BackupMetadata",
    "BackupType",
    "BackupError",
    "SnapshotManager",
    "SystemSnapshot",
    "get_backup_manager",
    "get_snapshot_manager",
    "create_backup",
    "restore_backup",
    "list_backups",
]
