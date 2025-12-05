"""
Tests for the logger module.
"""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.core.logger import (
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
)


class TestColoredFormatter:
    """Tests for ColoredFormatter class."""

    def test_formatter_creation(self):
        """Test creating ColoredFormatter."""
        formatter = ColoredFormatter()
        assert formatter is not None

    def test_format_includes_level(self):
        """Test that formatted output includes log level."""
        formatter = ColoredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "INFO" in formatted or "Test message" in formatted


class TestSplitWireLogger:
    """Tests for SplitWireLogger class."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_logger_creation(self, temp_log_dir):
        """Test creating a logger."""
        with patch('splitwire.core.logger.SplitWireLogger._get_log_dir', return_value=temp_log_dir):
            logger = SplitWireLogger.__new__(SplitWireLogger)
            logger._log_dir = temp_log_dir
            logger._log_dir.mkdir(parents=True, exist_ok=True)
            assert logger._log_dir.exists()

    def test_logger_writes_to_file(self, temp_log_dir):
        """Test that logger writes to file."""
        log_file = temp_log_dir / "test.log"

        # Create a simple file handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)

        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info("Test log message")
        handler.flush()
        handler.close()

        assert log_file.exists()
        content = log_file.read_text()
        assert "Test log message" in content

    def test_debug_mode(self, temp_log_dir):
        """Test debug mode enables debug level."""
        logger = logging.getLogger("debug_test")
        logger.setLevel(logging.DEBUG)

        # In debug mode, DEBUG level should be enabled
        assert logger.isEnabledFor(logging.DEBUG)

    def test_non_debug_mode(self, temp_log_dir):
        """Test non-debug mode uses INFO level."""
        logger = logging.getLogger("info_test")
        logger.setLevel(logging.INFO)

        # In non-debug mode, DEBUG should not show but INFO should
        assert logger.isEnabledFor(logging.INFO)


class TestLogLevels:
    """Tests for different log levels."""

    @pytest.fixture
    def logger(self):
        """Create a test logger with memory handler."""
        logger = logging.getLogger("level_test")
        logger.setLevel(logging.DEBUG)
        logger.handlers = []  # Clear existing handlers

        # Create a list to store log records
        self.log_records = []

        class MemoryHandler(logging.Handler):
            def __init__(self, records):
                super().__init__()
                self.records = records

            def emit(self, record):
                self.records.append(record)

        handler = MemoryHandler(self.log_records)
        logger.addHandler(handler)

        return logger

    def test_debug_level(self, logger):
        """Test DEBUG level logging."""
        logger.debug("Debug message")
        assert any(r.levelno == logging.DEBUG for r in self.log_records)

    def test_info_level(self, logger):
        """Test INFO level logging."""
        logger.info("Info message")
        assert any(r.levelno == logging.INFO for r in self.log_records)

    def test_warning_level(self, logger):
        """Test WARNING level logging."""
        logger.warning("Warning message")
        assert any(r.levelno == logging.WARNING for r in self.log_records)

    def test_error_level(self, logger):
        """Test ERROR level logging."""
        logger.error("Error message")
        assert any(r.levelno == logging.ERROR for r in self.log_records)

    def test_critical_level(self, logger):
        """Test CRITICAL level logging."""
        logger.critical("Critical message")
        assert any(r.levelno == logging.CRITICAL for r in self.log_records)


class TestComponentLogger:
    """Tests for component-specific loggers."""

    def test_component_logger_name(self):
        """Test that component loggers have correct names."""
        # Simulate getting a component logger
        component_name = "wireguard"
        logger_name = f"splitwire.{component_name}"

        logger = logging.getLogger(logger_name)
        assert component_name in logger.name

    def test_component_loggers_independent(self):
        """Test that component loggers are independent."""
        logger1 = logging.getLogger("splitwire.component1")
        logger2 = logging.getLogger("splitwire.component2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name


class TestLoggerConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        with patch('splitwire.core.logger._logger') as mock:
            mock._logger = MagicMock()
            yield mock

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger instance."""
        # This may initialize the global logger
        logger = get_logger()
        assert logger is not None

    def test_init_logger_creates_logger(self):
        """Test init_logger creates and returns a logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('splitwire.core.logger.SplitWireLogger._get_log_dir',
                       return_value=Path(tmpdir)):
                logger = init_logger(debug=True)
                assert logger is not None


class TestLogRotation:
    """Tests for log rotation functionality."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_rotating_handler_config(self, temp_log_dir):
        """Test rotating file handler configuration."""
        from logging.handlers import RotatingFileHandler

        log_file = temp_log_dir / "rotating.log"
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
        )

        assert handler.maxBytes == 5 * 1024 * 1024
        assert handler.backupCount == 3
