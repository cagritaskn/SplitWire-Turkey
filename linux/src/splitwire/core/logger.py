"""
Logging module for SplitWire-Turkey Linux.

Provides structured logging with file rotation and console output.
Logs are stored in ~/.cache/splitwire/logs/
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        result = super().format(record)

        # Restore original levelname
        record.levelname = levelname
        return result


class SplitWireLogger:
    """
    Application logger with file and console handlers.

    Features:
    - Rotating file logs (max 5MB, 3 backups)
    - Colored console output
    - Separate logs for different components
    - Debug mode toggle
    """

    APP_NAME = "splitwire"
    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
    BACKUP_COUNT = 3

    # Log format
    FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        name: str = APP_NAME,
        log_dir: Optional[Path] = None,
        debug: bool = False,
        console: bool = True
    ):
        """
        Initialize logger.

        Args:
            name: Logger name
            log_dir: Override log directory
            debug: Enable debug logging
            console: Enable console output
        """
        self._name = name
        self._debug = debug
        self._console_enabled = console

        # Determine log directory
        if log_dir:
            self._log_dir = log_dir
        else:
            # Default: ~/.cache/splitwire/logs
            xdg_cache = Path.home() / ".cache"
            self._log_dir = xdg_cache / self.APP_NAME / "logs"

        self._log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Remove existing handlers
        self._logger.handlers.clear()

        # Setup handlers
        self._setup_file_handler()
        if console:
            self._setup_console_handler()

    def _setup_file_handler(self) -> None:
        """Setup rotating file handler."""
        log_file = self._log_dir / f"{self._name}.log"

        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.MAX_LOG_SIZE,
            backupCount=self.BACKUP_COUNT,
            encoding="utf-8"
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT))

        self._logger.addHandler(handler)

    def _setup_console_handler(self) -> None:
        """Setup colored console handler."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if self._debug else logging.INFO)
        handler.setFormatter(ColoredFormatter(self.CONSOLE_FORMAT, self.DATE_FORMAT))

        self._logger.addHandler(handler)

    @property
    def logger(self) -> logging.Logger:
        """Get the underlying Logger instance."""
        return self._logger

    @property
    def log_dir(self) -> Path:
        """Get log directory path."""
        return self._log_dir

    @property
    def log_file(self) -> Path:
        """Get main log file path."""
        return self._log_dir / f"{self._name}.log"

    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug logging."""
        self._debug = enabled
        level = logging.DEBUG if enabled else logging.INFO
        self._logger.setLevel(level)

        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)

    # Logging methods

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, *args, **kwargs)

    # Component loggers

    def get_component_logger(self, component: str) -> "SplitWireLogger":
        """
        Get a logger for a specific component.

        Args:
            component: Component name (e.g., "wireguard", "zapret")

        Returns:
            Logger for the component
        """
        return SplitWireLogger(
            name=f"{self._name}.{component}",
            log_dir=self._log_dir,
            debug=self._debug,
            console=self._console_enabled
        )

    # Utility methods

    def get_recent_logs(self, lines: int = 100) -> list[str]:
        """
        Get recent log entries.

        Args:
            lines: Number of lines to retrieve

        Returns:
            List of log lines
        """
        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except IOError:
            return []

    def clear_logs(self) -> bool:
        """
        Clear all log files.

        Returns:
            True if successful
        """
        try:
            for log_file in self._log_dir.glob("*.log*"):
                log_file.unlink()
            return True
        except IOError:
            return False

    def get_log_size(self) -> int:
        """
        Get total size of log files in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for log_file in self._log_dir.glob("*.log*"):
            total += log_file.stat().st_size
        return total


# Global logger instance
_main_logger: Optional[SplitWireLogger] = None


def get_logger() -> SplitWireLogger:
    """Get the global logger instance."""
    global _main_logger
    if _main_logger is None:
        _main_logger = SplitWireLogger()
    return _main_logger


def init_logger(debug: bool = False, log_dir: Optional[Path] = None) -> SplitWireLogger:
    """
    Initialize the global logger.

    Args:
        debug: Enable debug mode
        log_dir: Override log directory

    Returns:
        The initialized logger
    """
    global _main_logger
    _main_logger = SplitWireLogger(debug=debug, log_dir=log_dir)
    return _main_logger


def get_component_logger(component: str) -> SplitWireLogger:
    """Get a logger for a specific component."""
    return get_logger().get_component_logger(component)


# Convenience functions
def debug(message: str, *args, **kwargs) -> None:
    """Log debug message."""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """Log info message."""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """Log warning message."""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """Log error message."""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs) -> None:
    """Log critical message."""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs) -> None:
    """Log exception with traceback."""
    get_logger().exception(message, *args, **kwargs)


if __name__ == "__main__":
    # Test the logger
    print("=" * 50)
    print("Logger Test")
    print("=" * 50)

    # Initialize with debug mode
    logger = init_logger(debug=True)

    print(f"\nLog directory: {logger.log_dir}")
    print(f"Log file: {logger.log_file}")

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Caught an exception")

    # Test component logger
    wg_logger = logger.get_component_logger("wireguard")
    wg_logger.info("WireGuard component initialized")

    zapret_logger = get_component_logger("zapret")
    zapret_logger.info("Zapret component initialized")

    # Test convenience functions
    info("Using convenience function")
    debug("Debug via convenience function")

    # Test log retrieval
    print("\n--- Recent logs ---")
    recent = logger.get_recent_logs(5)
    for line in recent:
        print(line.strip())

    print(f"\nTotal log size: {logger.get_log_size()} bytes")
    print("\nTest completed!")
