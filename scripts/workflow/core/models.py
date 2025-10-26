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
