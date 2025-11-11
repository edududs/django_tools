"""Core data models for workflow execution."""

from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of a command execution."""

    name: str
    command: str
    success: bool
    duration: float
    output: str
    error: str


@dataclass
class JobResult:
    """Result of a job execution."""

    name: str
    success: bool
    duration: float
    commands: list[CommandResult]


@dataclass
class ExecutionResult:
    """Pure execution result without presentation.

    This is the result from infrastructure/command_executor,
    before any presentation/formatting is applied.
    """

    success: bool
    returncode: int
    stdout: str
    stderr: str
    duration: float
