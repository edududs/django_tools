"""Command execution - pure subprocess execution without presentation."""

import subprocess
import time
from pathlib import Path

from ..types import ExecutionResult


def execute_command(
    command: str,
    cwd: Path,
    timeout: float | None = None,
    stream_output: bool = False,
) -> ExecutionResult:
    """Execute a shell command and return structured result.

    Pure function - no console output, no presentation.
    All output is captured and returned in ExecutionResult.

    Args:
        command: Shell command to execute
        cwd: Working directory for command execution
        timeout: Optional timeout in seconds
        stream_output: If True, stream output to stdout in real-time (still captures)

    Returns:
        ExecutionResult with execution details

    """
    start_time = time.time()

    try:
        result = subprocess.run(  # noqa: S602
            command,
            shell=True,
            cwd=cwd,
            capture_output=not stream_output,
            text=True,
            check=False,
            timeout=timeout,
        )

        duration = time.time() - start_time

        # If streaming, stdout/stderr are None, capture separately
        if stream_output:
            stdout = ""
            stderr = ""
        else:
            stdout = result.stdout or ""
            stderr = result.stderr or ""

        return ExecutionResult(
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
        )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return ExecutionResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            duration=duration,
        )

    except Exception as e:
        duration = time.time() - start_time
        return ExecutionResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr=str(e),
            duration=duration,
        )
