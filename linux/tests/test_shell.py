"""
Tests for the shell executor module.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.core.shell import (
    ShellExecutor,
    CommandResult,
    CommandStatus,
    run,
    run_async,
    command_exists,
)


class TestCommandStatus:
    """Tests for CommandStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert CommandStatus.SUCCESS.value == "success"
        assert CommandStatus.FAILED.value == "failed"
        assert CommandStatus.TIMEOUT.value == "timeout"
        assert CommandStatus.CANCELLED.value == "cancelled"
        assert CommandStatus.NOT_FOUND.value == "not_found"


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_success_property(self):
        """Test success property returns True for successful commands."""
        result = CommandResult(
            status=CommandStatus.SUCCESS,
            returncode=0,
            stdout="output",
            stderr="",
            command="echo test",
        )
        assert result.success is True

    def test_success_property_failed(self):
        """Test success property returns False for failed commands."""
        result = CommandResult(
            status=CommandStatus.FAILED,
            returncode=1,
            stdout="",
            stderr="error",
            command="false",
        )
        assert result.success is False

    def test_output_property(self):
        """Test output property combines stdout and stderr."""
        result = CommandResult(
            status=CommandStatus.SUCCESS,
            returncode=0,
            stdout="standard output",
            stderr="error output",
            command="test",
        )
        output = result.output
        assert "standard output" in output
        assert "error output" in output

    def test_duration_default(self):
        """Test duration defaults to 0."""
        result = CommandResult(
            status=CommandStatus.SUCCESS,
            returncode=0,
            stdout="",
            stderr="",
            command="test",
        )
        assert result.duration == 0.0


class TestShellExecutor:
    """Tests for ShellExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create a ShellExecutor instance."""
        return ShellExecutor(timeout=10)

    def test_run_simple_command(self, executor):
        """Test running a simple command."""
        result = executor.run("echo 'Hello World'")
        assert result.success is True
        assert "Hello World" in result.stdout

    def test_run_command_with_args(self, executor):
        """Test running command with arguments."""
        result = executor.run(["echo", "test", "args"])
        assert result.success is True
        assert "test args" in result.stdout

    def test_run_failed_command(self, executor):
        """Test handling of failed command."""
        result = executor.run("false")  # 'false' command always returns 1
        assert result.success is False
        assert result.returncode == 1

    def test_run_command_not_found(self, executor):
        """Test handling of non-existent command."""
        result = executor.run("nonexistent_command_xyz123")
        assert result.status == CommandStatus.NOT_FOUND

    def test_run_with_timeout(self, executor):
        """Test command timeout handling."""
        result = executor.run("sleep 5", timeout=1)
        assert result.status == CommandStatus.TIMEOUT

    def test_run_capture_stderr(self, executor):
        """Test capturing stderr output."""
        result = executor.run("ls /nonexistent_path_xyz")
        assert result.success is False
        assert result.stderr != ""

    def test_command_exists_true(self, executor):
        """Test command_exists for existing command."""
        assert executor.command_exists("echo") is True

    def test_command_exists_false(self, executor):
        """Test command_exists for non-existing command."""
        assert executor.command_exists("nonexistent_cmd_xyz") is False

    def test_get_command_path(self, executor):
        """Test getting command path."""
        path = executor.get_command_path("echo")
        assert path is not None
        assert "echo" in path

    def test_get_command_path_not_found(self, executor):
        """Test get_command_path for non-existing command."""
        path = executor.get_command_path("nonexistent_cmd_xyz")
        assert path is None

    def test_run_with_env(self, executor):
        """Test running command with custom environment."""
        result = executor.run(
            "echo $TEST_VAR",
            env={"TEST_VAR": "custom_value"},
            shell=True
        )
        assert result.success is True
        assert "custom_value" in result.stdout

    def test_run_with_cwd(self, executor):
        """Test running command in specific directory."""
        result = executor.run("pwd", cwd=Path("/tmp"))
        assert result.success is True
        assert "/tmp" in result.stdout


class TestAsyncExecution:
    """Tests for async command execution."""

    @pytest.fixture
    def executor(self):
        """Create a ShellExecutor instance."""
        return ShellExecutor(timeout=10)

    @pytest.mark.asyncio
    async def test_run_async_simple(self, executor):
        """Test async command execution."""
        result = await executor.run_async("echo 'async test'")
        assert result.success is True
        assert "async test" in result.stdout

    @pytest.mark.asyncio
    async def test_run_async_timeout(self, executor):
        """Test async command timeout."""
        result = await executor.run_async("sleep 5", timeout=1)
        assert result.status == CommandStatus.TIMEOUT

    @pytest.mark.asyncio
    async def test_run_async_failed(self, executor):
        """Test async handling of failed command."""
        result = await executor.run_async("false")
        assert result.success is False


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_run_function(self):
        """Test the run() convenience function."""
        result = run("echo 'convenience test'")
        assert result.success is True
        assert "convenience test" in result.stdout

    def test_command_exists_function(self):
        """Test the command_exists() convenience function."""
        assert command_exists("echo") is True
        assert command_exists("nonexistent_xyz") is False

    @pytest.mark.asyncio
    async def test_run_async_function(self):
        """Test the run_async() convenience function."""
        result = await run_async("echo 'async convenience'")
        assert result.success is True


class TestStreamingOutput:
    """Tests for streaming output functionality."""

    @pytest.fixture
    def executor(self):
        """Create a ShellExecutor instance."""
        return ShellExecutor(timeout=10)

    def test_run_with_output_callback(self, executor):
        """Test running command with output callback."""
        lines = []

        def callback(line):
            lines.append(line)

        result = executor.run_with_output(
            ["echo", "-e", "line1\\nline2\\nline3"],
            callback=callback,
        )

        assert result.success is True
        # The callback should have been called for each line
        assert len(lines) >= 1
