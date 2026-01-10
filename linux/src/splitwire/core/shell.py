"""
Shell command execution module for SplitWire-Turkey Linux.

Provides safe shell command execution with:
- Timeout handling
- Output capture
- Async execution
- Privilege elevation integration
"""

import asyncio
import os
import shlex
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Union
import threading


class CommandStatus(Enum):
    """Status of command execution."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    NOT_FOUND = "not_found"


@dataclass
class CommandResult:
    """Result of a shell command execution."""
    status: CommandStatus
    returncode: int
    stdout: str
    stderr: str
    command: str
    duration: float = 0.0

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.status == CommandStatus.SUCCESS and self.returncode == 0

    @property
    def output(self) -> str:
        """Get combined stdout and stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


class ShellExecutor:
    """
    Executes shell commands with various options.

    Features:
    - Synchronous and asynchronous execution
    - Timeout handling
    - Output streaming
    - Environment variable management
    - Working directory control
    """

    DEFAULT_TIMEOUT = 60  # seconds

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        env: Optional[dict[str, str]] = None,
        cwd: Optional[Path] = None
    ):
        """
        Initialize shell executor.

        Args:
            timeout: Default command timeout in seconds
            env: Additional environment variables
            cwd: Default working directory
        """
        self._timeout = timeout
        self._env = self._build_env(env)
        self._cwd = cwd

    def _build_env(self, extra_env: Optional[dict[str, str]] = None) -> dict[str, str]:
        """Build environment dictionary."""
        env = os.environ.copy()

        # Ensure PATH includes common locations
        paths = ["/usr/local/bin", "/usr/bin", "/bin", "/usr/local/sbin", "/usr/sbin", "/sbin"]
        current_path = env.get("PATH", "")
        for p in paths:
            if p not in current_path:
                current_path = f"{p}:{current_path}"
        env["PATH"] = current_path

        # Add extra environment variables
        if extra_env:
            env.update(extra_env)

        return env

    def run(
        self,
        command: Union[str, list[str]],
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = False,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
        shell: bool = False,
        input_data: Optional[str] = None
    ) -> CommandResult:
        """
        Run a command synchronously.

        Args:
            command: Command string or list of arguments
            timeout: Command timeout (overrides default)
            capture_output: Whether to capture stdout/stderr
            check: Raise exception on non-zero return code
            cwd: Working directory (overrides default)
            env: Additional environment variables
            shell: Run through shell
            input_data: Data to send to command's stdin

        Returns:
            CommandResult with execution details
        """
        import time
        start_time = time.time()

        # Parse command
        if isinstance(command, str):
            cmd_str = command
            if shell:
                cmd = command
            else:
                cmd = shlex.split(command)
        else:
            cmd_str = " ".join(command)
            cmd = command

        # Build environment
        run_env = self._env.copy()
        if env:
            run_env.update(env)

        # Determine working directory
        run_cwd = cwd or self._cwd

        # Set timeout
        run_timeout = timeout if timeout is not None else self._timeout

        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=run_timeout,
                    cwd=run_cwd,
                    env=run_env,
                    shell=shell,
                    input=input_data
                )
                stdout = result.stdout
                stderr = result.stderr
            else:
                result = subprocess.run(
                    cmd,
                    timeout=run_timeout,
                    cwd=run_cwd,
                    env=run_env,
                    shell=shell,
                    input=input_data,
                    text=True if input_data else False
                )
                stdout = ""
                stderr = ""

            duration = time.time() - start_time

            status = CommandStatus.SUCCESS if result.returncode == 0 else CommandStatus.FAILED

            cmd_result = CommandResult(
                status=status,
                returncode=result.returncode,
                stdout=stdout.strip() if stdout else "",
                stderr=stderr.strip() if stderr else "",
                command=cmd_str,
                duration=duration
            )

            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode, cmd_str, stdout, stderr
                )

            return cmd_result

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.TIMEOUT,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {run_timeout} seconds",
                command=cmd_str,
                duration=duration
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.NOT_FOUND,
                returncode=-1,
                stdout="",
                stderr=f"Command not found: {cmd[0] if isinstance(cmd, list) else cmd.split()[0]}",
                command=cmd_str,
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.FAILED,
                returncode=-1,
                stdout="",
                stderr=str(e),
                command=cmd_str,
                duration=duration
            )

    async def run_async(
        self,
        command: Union[str, list[str]],
        timeout: Optional[int] = None,
        capture_output: bool = True,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None
    ) -> CommandResult:
        """
        Run a command asynchronously.

        Args:
            command: Command string or list of arguments
            timeout: Command timeout
            capture_output: Whether to capture stdout/stderr
            cwd: Working directory
            env: Additional environment variables

        Returns:
            CommandResult with execution details
        """
        import time
        start_time = time.time()

        # Parse command
        if isinstance(command, str):
            cmd_str = command
            cmd = shlex.split(command)
        else:
            cmd_str = " ".join(command)
            cmd = command

        # Build environment
        run_env = self._env.copy()
        if env:
            run_env.update(env)

        # Determine working directory
        run_cwd = str(cwd or self._cwd) if (cwd or self._cwd) else None

        # Set timeout
        run_timeout = timeout if timeout is not None else self._timeout

        try:
            if capture_output:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=run_cwd,
                    env=run_env
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=run_cwd,
                    env=run_env
                )

            try:
                if capture_output:
                    stdout_bytes, stderr_bytes = await asyncio.wait_for(
                        process.communicate(),
                        timeout=run_timeout
                    )
                    stdout = stdout_bytes.decode("utf-8", errors="replace")
                    stderr = stderr_bytes.decode("utf-8", errors="replace")
                else:
                    await asyncio.wait_for(process.wait(), timeout=run_timeout)
                    stdout = ""
                    stderr = ""

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                duration = time.time() - start_time
                return CommandResult(
                    status=CommandStatus.TIMEOUT,
                    returncode=-1,
                    stdout="",
                    stderr=f"Command timed out after {run_timeout} seconds",
                    command=cmd_str,
                    duration=duration
                )

            duration = time.time() - start_time
            status = CommandStatus.SUCCESS if process.returncode == 0 else CommandStatus.FAILED

            return CommandResult(
                status=status,
                returncode=process.returncode or 0,
                stdout=stdout.strip() if stdout else "",
                stderr=stderr.strip() if stderr else "",
                command=cmd_str,
                duration=duration
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.NOT_FOUND,
                returncode=-1,
                stdout="",
                stderr=f"Command not found: {cmd[0]}",
                command=cmd_str,
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.FAILED,
                returncode=-1,
                stdout="",
                stderr=str(e),
                command=cmd_str,
                duration=duration
            )

    def run_with_output(
        self,
        command: Union[str, list[str]],
        callback: Callable[[str], None],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None
    ) -> CommandResult:
        """
        Run a command with real-time output streaming.

        Args:
            command: Command string or list of arguments
            callback: Function to call with each line of output
            timeout: Command timeout
            cwd: Working directory
            env: Additional environment variables

        Returns:
            CommandResult with execution details
        """
        import time
        start_time = time.time()

        # Parse command
        if isinstance(command, str):
            cmd_str = command
            cmd = shlex.split(command)
        else:
            cmd_str = " ".join(command)
            cmd = command

        # Build environment
        run_env = self._env.copy()
        if env:
            run_env.update(env)

        # Determine working directory
        run_cwd = cwd or self._cwd

        # Set timeout
        run_timeout = timeout if timeout is not None else self._timeout

        stdout_lines = []
        stderr_lines = []

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=run_cwd,
                env=run_env,
                bufsize=1
            )

            # Read output with timeout
            def read_output():
                for line in iter(process.stdout.readline, ""):
                    if line:
                        stdout_lines.append(line.rstrip())
                        callback(line.rstrip())
                process.stdout.close()

            reader_thread = threading.Thread(target=read_output)
            reader_thread.start()
            reader_thread.join(timeout=run_timeout)

            if reader_thread.is_alive():
                process.kill()
                reader_thread.join()
                duration = time.time() - start_time
                return CommandResult(
                    status=CommandStatus.TIMEOUT,
                    returncode=-1,
                    stdout="\n".join(stdout_lines),
                    stderr=f"Command timed out after {run_timeout} seconds",
                    command=cmd_str,
                    duration=duration
                )

            returncode = process.wait()
            duration = time.time() - start_time

            status = CommandStatus.SUCCESS if returncode == 0 else CommandStatus.FAILED

            return CommandResult(
                status=status,
                returncode=returncode,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
                command=cmd_str,
                duration=duration
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.NOT_FOUND,
                returncode=-1,
                stdout="",
                stderr=f"Command not found: {cmd[0]}",
                command=cmd_str,
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return CommandResult(
                status=CommandStatus.FAILED,
                returncode=-1,
                stdout="\n".join(stdout_lines),
                stderr=str(e),
                command=cmd_str,
                duration=duration
            )

    def command_exists(self, command: str) -> bool:
        """
        Check if a command exists in PATH.

        Args:
            command: Command name

        Returns:
            True if command exists
        """
        result = self.run(["which", command], timeout=5)
        return result.success

    def get_command_path(self, command: str) -> Optional[str]:
        """
        Get full path of a command.

        Args:
            command: Command name

        Returns:
            Full path or None if not found
        """
        result = self.run(["which", command], timeout=5)
        if result.success:
            return result.stdout
        return None


# Global instance
_shell: Optional[ShellExecutor] = None


def get_shell() -> ShellExecutor:
    """Get the global ShellExecutor instance."""
    global _shell
    if _shell is None:
        _shell = ShellExecutor()
    return _shell


def run(command: Union[str, list[str]], **kwargs) -> CommandResult:
    """Run a command (convenience function)."""
    return get_shell().run(command, **kwargs)


async def run_async(command: Union[str, list[str]], **kwargs) -> CommandResult:
    """Run a command asynchronously (convenience function)."""
    return await get_shell().run_async(command, **kwargs)


def command_exists(command: str) -> bool:
    """Check if a command exists (convenience function)."""
    return get_shell().command_exists(command)


if __name__ == "__main__":
    # Test the shell executor
    print("=" * 50)
    print("ShellExecutor Test")
    print("=" * 50)

    shell = ShellExecutor()

    # Test basic command
    print("\n--- Basic command ---")
    result = shell.run("echo 'Hello, World!'")
    print(f"Status: {result.status.value}")
    print(f"Output: {result.stdout}")
    print(f"Duration: {result.duration:.3f}s")

    # Test command with arguments
    print("\n--- Command with args ---")
    result = shell.run(["ls", "-la", "/tmp"])
    print(f"Status: {result.status.value}")
    print(f"Return code: {result.returncode}")
    print(f"Lines: {len(result.stdout.splitlines())}")

    # Test command_exists
    print("\n--- Command exists ---")
    print(f"python3 exists: {shell.command_exists('python3')}")
    print(f"nonexistent exists: {shell.command_exists('nonexistent_command_xyz')}")

    # Test get_command_path
    print("\n--- Command path ---")
    print(f"python3 path: {shell.get_command_path('python3')}")

    # Test timeout
    print("\n--- Timeout test ---")
    result = shell.run("sleep 5", timeout=1)
    print(f"Status: {result.status.value}")
    print(f"Error: {result.stderr}")

    # Test streaming output
    print("\n--- Streaming output ---")
    def output_callback(line):
        print(f"  > {line}")

    result = shell.run_with_output(
        "for i in 1 2 3; do echo Line $i; sleep 0.1; done",
        output_callback,
        shell=False
    )
    # Need to use shell=True for this
    result = shell.run(
        "for i in 1 2 3; do echo Line $i; sleep 0.1; done",
        shell=True
    )
    print(f"Final output:\n{result.stdout}")

    # Test async
    print("\n--- Async test ---")
    async def test_async():
        result = await shell.run_async("uname -a")
        print(f"Async result: {result.stdout}")

    asyncio.run(test_async())

    print("\nTest completed!")
