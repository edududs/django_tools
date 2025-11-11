"""Renderers - render results to console."""

from pathlib import Path

from ..types import ConfigData, ExecutionResult, JobResult
from .console import ConsoleInterface
from .formatters import (
    create_panel,
    format_command_line,
    format_command_name,
    format_duration,
    format_status,
)


def render_command_execution(
    console: ConsoleInterface,
    name: str,
    command: str,
    result: ExecutionResult,
    show_output: bool = True,
) -> None:
    """Render command execution result.

    Args:
        console: Console interface
        name: Command name
        command: Command line
        result: Execution result
        show_output: Whether to show output

    """
    console.print(format_command_name(name))
    console.print(format_command_line(command))

    if show_output:
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print_warning(result.stderr)

    status = format_status(result.success)
    duration = format_duration(result.duration)
    console.print(f"{status} {name} {duration}")


def render_job_result(console: ConsoleInterface, job: JobResult) -> None:
    """Render job result.

    Args:
        console: Console interface
        job: Job result

    """
    status = format_status(job.success)
    duration = format_duration(job.duration)
    console.print(f"{status} {job.name} {duration}")


def render_config(console: ConsoleInterface, config: ConfigData, config_file: Path) -> None:
    """Render configuration.

    Args:
        console: Console interface
        config: Configuration data
        config_file: Config file path

    """
    if not config.env_root and not config.target_path:
        console.print_warning("No configuration found.")
        console.print("\n[dim]Use 'workflow config set-env' to configure an environment.[/dim]")
        return

    console.print("[bold cyan]Current Configuration:[/bold cyan]\n")

    if config.env_root:
        console.print_success(f"Environment Root: {config.env_root}")
    else:
        console.print("[dim]Environment Root: Not configured[/dim]")

    if config.target_path:
        console.print_success(f"Target Path: {config.target_path}")
    else:
        console.print("[dim]Target Path: Not configured[/dim]")

    console.print(f"\n[dim]Config file: {config_file}[/dim]")


def render_validation_summary(console: ConsoleInterface, results: list[JobResult]) -> None:
    """Render validation summary.

    Args:
        console: Console interface
        results: List of job results

    """
    for job in results:
        render_job_result(console, job)

    all_success = all(job.success for job in results)
    if all_success:
        console.print_success("\n✓ All validations passed!")
    else:
        console.print_error("\n✗ Some validations failed")

