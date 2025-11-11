"""Quality check commands (ruff, pyright, tests)."""

import time
from pathlib import Path

from ..domain.validation import create_validation_plan
from ..infrastructure import execute_command
from ..presentation import (
    RichConsole,
    render_command_execution,
    render_validation_summary,
)
from ..types import CommandResult, JobResult

console = RichConsole()


def _run_ruff_job(
    project_root: Path,
    target_path: Path | None = None,
    fix: bool = False,
    show_output: bool = True,
) -> JobResult:
    """Run Ruff linting checks.

    Args:
        project_root: Project root directory
        target_path: Optional target directory to check (defaults to src/)
        fix: Whether to auto-fix issues
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    console.print_panel("[bold blue]Ruff Check[/bold blue]", style="blue")

    start_time = time.time()
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

    commands: list[CommandResult] = []
    for name, cmd in command_specs:
        result = execute_command(cmd, cwd=project_root, stream_output=show_output)
        render_command_execution(console, name, cmd, result, show_output=show_output)

        commands.append(
            CommandResult(
                name=name,
                command=cmd,
                success=result.success,
                duration=result.duration,
                output=result.stdout,
                error=result.stderr,
            )
        )

    duration = time.time() - start_time
    success = all(cmd.success for cmd in commands)

    return JobResult(name="ruff", success=success, duration=duration, commands=commands)


def _run_pyright_job(project_root: Path, show_output: bool = True) -> JobResult:
    """Run Pyright type checking.

    Args:
        project_root: Project root directory
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    console.print_panel("[bold magenta]Pyright Check[/bold magenta]", style="magenta")

    start_time = time.time()

    result = execute_command("pyright", cwd=project_root, stream_output=show_output)
    render_command_execution(
        console, "Run Pyright type checking", "pyright", result, show_output=show_output
    )

    commands = [
        CommandResult(
            name="Run Pyright type checking",
            command="pyright",
            success=result.success,
            duration=result.duration,
            output=result.stdout,
            error=result.stderr,
        )
    ]

    duration = time.time() - start_time
    success = result.success

    return JobResult(name="pyright", success=success, duration=duration, commands=commands)


def _run_tests_job(project_root: Path, show_output: bool = True) -> JobResult:
    """Run pytest tests with coverage.

    Args:
        project_root: Project root directory
        show_output: Whether to show command output

    Returns:
        JobResult with test results

    """
    console.print_panel("[bold green]Tests[/bold green]", style="green")

    start_time = time.time()

    cmd = "uv run pytest src/ -v --cov=src --cov-report=term-missing"
    result = execute_command(cmd, cwd=project_root, stream_output=show_output)
    render_command_execution(
        console, "Run tests with coverage", cmd, result, show_output=show_output
    )

    commands = [
        CommandResult(
            name="Run tests with coverage",
            command=cmd,
            success=result.success,
            duration=result.duration,
            output=result.stdout,
            error=result.stderr,
        )
    ]

    duration = time.time() - start_time
    success = result.success

    return JobResult(name="tests", success=success, duration=duration, commands=commands)


def check_command(
    project_root: Path,
    ruff: bool = True,
    pyright: bool = False,
    tests: bool = False,
    fix: bool = False,
    target_path: Path | None = None,
) -> bool:
    """Run quality checks.

    Args:
        project_root: Project root directory
        ruff: Run Ruff checks
        pyright: Run Pyright checks
        tests: Run tests
        fix: Auto-fix issues where possible
        target_path: Optional target path for validation

    Returns:
        True if all checks passed, False otherwise

    """
    plan = create_validation_plan(ruff=ruff, pyright=pyright, tests=tests)
    results: list[JobResult] = []

    # Run Ruff checks
    if plan.ruff:
        result = _run_ruff_job(project_root, target_path=target_path, fix=fix)
        results.append(result)
        if not result.success:
            console.print_error("\nRuff checks failed.")

    # Run Pyright checks
    if plan.pyright:
        result = _run_pyright_job(project_root)
        results.append(result)
        if not result.success:
            console.print_warning("\nPyright checks failed (continuing...).")

    # Run tests
    if plan.tests:
        result = _run_tests_job(project_root)
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
