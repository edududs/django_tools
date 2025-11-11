"""Quality check commands (ruff, pyright, tests)."""

from contextlib import contextmanager
from pathlib import Path

from ..domain.validation import ValidationPlan
from ..infrastructure import execute_command
from ..presentation import (
    ConsoleInterface,
    RichConsole,
    render_command_execution,
    render_validation_summary,
)
from ..types import CommandResult, ExecutionResult, JobResult


@contextmanager
def _measure_time():
    """Context manager for measuring execution time."""
    from time import perf_counter

    start = perf_counter()
    yield lambda: perf_counter() - start


def _create_command_result(name: str, command: str, result: ExecutionResult) -> CommandResult:
    """Create CommandResult from ExecutionResult.

    Args:
        name: Command name
        command: Command string
        result: ExecutionResult

    Returns:
        CommandResult

    """
    return CommandResult(
        name=name,
        command=command,
        success=result.success,
        duration=result.duration,
        output=result.stdout,
        error=result.stderr,
    )


def _run_single_command_job(
    project_root: Path,
    console: ConsoleInterface,
    job_name: str,
    panel_title: str,
    panel_style: str,
    command: str,
    command_name: str,
    show_output: bool = True,
) -> JobResult:
    """Run a job with a single command.

    Args:
        project_root: Project root directory
        console: Console interface for output
        job_name: Job identifier
        panel_title: Panel title for display
        panel_style: Panel style
        command: Command to execute
        command_name: Display name for command
        show_output: Whether to show command output

    Returns:
        JobResult

    """
    console.print_panel(panel_title, style=panel_style)

    with _measure_time() as get_duration:
        # Always capture output when using Textual - never stream directly to stdout/stderr
        result = execute_command(command, cwd=project_root, stream_output=False)
        render_command_execution(console, command_name, command, result, show_output=show_output)

        commands = [_create_command_result(command_name, command, result)]
        duration = get_duration()
        success = result.success

    return JobResult(name=job_name, success=success, duration=duration, commands=commands)


def _run_ruff_job(
    project_root: Path,
    console: ConsoleInterface,
    target_path: Path | None = None,
    fix: bool = False,
    show_output: bool = True,
) -> JobResult:
    """Run Ruff linting checks.

    Args:
        project_root: Project root directory
        console: Console interface for output
        target_path: Optional target directory to check (defaults to src/)
        fix: Whether to auto-fix issues
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    console.print_panel("[bold blue]Ruff Check[/bold blue]", style="blue")

    check_target = str(target_path) if target_path else "src/"

    # Build command list
    fix_flags = "--fix --unsafe-fixes" if fix else ""
    command_specs = [
        ("Verify Ruff installation", "uv run ruff --version"),
        ("Run Ruff linting", f"uv run ruff check {check_target} {fix_flags}".strip()),
        (
            "Run Ruff format" if fix else "Run Ruff format check",
            f"uv run ruff format {'' if fix else '--check'} {check_target}",
        ),
    ]

    with _measure_time() as get_duration:
        commands: list[CommandResult] = []
        for name, cmd in command_specs:
            # Always capture output when using Textual - never stream directly to stdout/stderr
            result = execute_command(cmd, cwd=project_root, stream_output=False)
            render_command_execution(console, name, cmd, result, show_output=show_output)
            commands.append(_create_command_result(name, cmd, result))

        duration = get_duration()
    success = all(cmd.success for cmd in commands)

    return JobResult(name="ruff", success=success, duration=duration, commands=commands)


def _run_pyright_job(
    project_root: Path, console: ConsoleInterface, show_output: bool = True
) -> JobResult:
    """Run Pyright type checking.

    Args:
        project_root: Project root directory
        console: Console interface for output
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    return _run_single_command_job(
        project_root=project_root,
        console=console,
        job_name="pyright",
        panel_title="[bold magenta]Pyright Check[/bold magenta]",
        panel_style="magenta",
        command="pyright",
        command_name="Run Pyright type checking",
        show_output=show_output,
    )


def _run_tests_job(
    project_root: Path, console: ConsoleInterface, show_output: bool = True
) -> JobResult:
    """Run pytest tests with coverage.

    Args:
        project_root: Project root directory
        console: Console interface for output
        show_output: Whether to show command output

    Returns:
        JobResult with test results

    """
    cmd = "uv run pytest src/ -v --cov=src --cov-report=term-missing"
    return _run_single_command_job(
        project_root=project_root,
        console=console,
        job_name="tests",
        panel_title="[bold green]Tests[/bold green]",
        panel_style="green",
        command=cmd,
        command_name="Run tests with coverage",
        show_output=show_output,
    )


def check_command(
    project_root: Path,
    console: ConsoleInterface | None = None,
    ruff: bool = True,
    pyright: bool = False,
    tests: bool = False,
    fix: bool = False,
    target_path: Path | None = None,
) -> bool:
    """Run quality checks.

    Args:
        project_root: Project root directory
        console: Console interface for output (defaults to RichConsole if None)
        ruff: Run Ruff checks
        pyright: Run Pyright checks
        tests: Run tests
        fix: Auto-fix issues where possible
        target_path: Optional target path for validation

    Returns:
        True if all checks passed, False otherwise

    """
    console = console or RichConsole()
    plan = ValidationPlan(ruff=ruff, pyright=pyright, tests=tests)
    results: list[JobResult] = []

    # Run Ruff checks
    if plan.ruff:
        result = _run_ruff_job(project_root, console, target_path=target_path, fix=fix)
        results.append(result)
        if not result.success:
            console.print_error("\nRuff checks failed.")

    # Run Pyright checks
    if plan.pyright:
        result = _run_pyright_job(project_root, console)
        results.append(result)
        if not result.success:
            console.print_warning("\nPyright checks failed (continuing...).")

    # Run tests
    if plan.tests:
        result = _run_tests_job(project_root, console)
        results.append(result)
        if not result.success:
            console.print_error("\nTests failed.")

    # Generate summary
    if not results:
        return True

    console.print("\n" + "=" * 80 + "\n")
    render_validation_summary(console, results)

    total_duration = sum(job.duration for job in results)
    all_success = all(job.success for job in results)

    console.print("\n" + "=" * 80 + "\n")

    if all_success:
        success_msg = f"[bold green]✓ All checks passed![/bold green]\n[dim]Total duration: {total_duration:.2f}s[/dim]"
        console.print_panel(success_msg, style="green")
        return True

    # Show summary of failed checks
    failed_jobs = [job for job in results if not job.success]
    error_msg = "[bold red]✗ Some checks failed[/bold red]\n\n"
    error_msg += "[yellow]Failed checks:[/yellow]\n"
    for job in failed_jobs:
        failed_commands = [cmd for cmd in job.commands if not cmd.success]
        error_msg += f"  • {job.name.upper()}: {len(failed_commands)} command(s) failed\n"
    error_msg += f"\n[dim]Total duration: {total_duration:.2f}s[/dim]"

    if fix:
        error_msg += (
            "\n[cyan]💡 Tip: Some issues were auto-fixed. Review changes before committing.[/cyan]"
        )
    else:
        error_msg += "\n[cyan]💡 Tip: Run with --fix to auto-fix some issues.[/cyan]"

    console.print_panel(error_msg, style="red")
    return False
