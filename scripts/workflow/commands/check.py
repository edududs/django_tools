"""Quality check commands (ruff, pyright, tests)."""

import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core import JobResult, WorkflowRunner

console = Console()


def _show_command_errors(check_name: str, commands: list) -> None:
    """Display errors from failed commands.

    Args:
        check_name: Name of the check (for display)
        commands: List of command results to check

    """
    console.print(f"\n[bold red]❌ {check_name} checks failed with errors:[/bold red]")
    for cmd in commands:
        if not cmd.success:
            console.print(f"\n[yellow]Failed command:[/yellow] {cmd.name}")
            if cmd.error:
                console.print(f"[red]{cmd.error}[/red]")
            if cmd.output:
                console.print(f"[dim]{cmd.output}[/dim]")


def run_ruff_check(
    runner: WorkflowRunner,
    target_path: Path | None = None,
    fix: bool = False,
    show_output: bool = True,
) -> JobResult:
    """Run Ruff linting checks.

    Args:
        runner: WorkflowRunner instance
        target_path: Optional target directory to check (defaults to src/)
        fix: Whether to auto-fix issues
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    console.print(Panel.fit("[bold blue]Ruff Check[/bold blue]", border_style="blue"))

    start_time = time.time()
    check_target = str(target_path) if target_path else "src/"

    # Build command list
    commands = [
        runner.run_command(
            "Verify Ruff installation",
            "uv run ruff --version",
            show_output=show_output,
        ),
        runner.run_command(
            "Run Ruff linting",
            f"uv run ruff check {check_target} {'--fix' if fix else ''}",
            show_output=show_output,
        ),
        runner.run_command(
            "Run Ruff format" if fix else "Run Ruff format check",
            f"uv run ruff format {'' if fix else '--check'} {check_target}",
            show_output=show_output,
        ),
    ]

    duration = time.time() - start_time
    success = all(cmd.success for cmd in commands)

    # Show errors for failed commands
    if not success:
        _show_command_errors("Ruff", commands)

    return JobResult(name="ruff", success=success, duration=duration, commands=commands)


def run_pyright_check(runner: WorkflowRunner, show_output: bool = True) -> JobResult:
    """Run Pyright type checking.

    Args:
        runner: WorkflowRunner instance
        show_output: Whether to show command output

    Returns:
        JobResult with check results

    """
    console.print(Panel.fit("[bold magenta]Pyright Check[/bold magenta]", border_style="magenta"))

    start_time = time.time()

    commands = [
        runner.run_command(
            "Run Pyright type checking",
            "pyright",
            show_output=show_output,
        ),
    ]

    duration = time.time() - start_time
    success = all(cmd.success for cmd in commands)

    # Show detailed errors if any command failed
    if not success:
        console.print("\n[bold red]❌ Pyright checks failed with errors:[/bold red]")
        for cmd in commands:
            if not cmd.success:
                console.print(f"\n[yellow]Failed command:[/yellow] {cmd.name}")
                if cmd.error:
                    console.print(f"[red]{cmd.error}[/red]")
                if cmd.output:
                    console.print(f"[dim]{cmd.output}[/dim]")

    return JobResult(name="pyright", success=success, duration=duration, commands=commands)


def run_tests(runner: WorkflowRunner, show_output: bool = True) -> JobResult:
    """Run pytest tests with coverage.

    Args:
        runner: WorkflowRunner instance
        show_output: Whether to show command output

    Returns:
        JobResult with test results

    """
    console.print(Panel.fit("[bold green]Tests[/bold green]", border_style="green"))

    start_time = time.time()

    commands = [
        runner.run_command(
            "Run tests with coverage",
            "uv run pytest src/ -v --cov=src --cov-report=term-missing",
            show_output=show_output,
        ),
    ]

    duration = time.time() - start_time
    success = all(cmd.success for cmd in commands)

    # Show detailed errors if any command failed
    if not success:
        console.print("\n[bold red]❌ Tests failed with errors:[/bold red]")
        for cmd in commands:
            if not cmd.success:
                console.print(f"\n[yellow]Failed command:[/yellow] {cmd.name}")
                if cmd.error:
                    console.print(f"[red]{cmd.error}[/red]")
                if cmd.output:
                    console.print(f"[dim]{cmd.output}[/dim]")

    return JobResult(name="tests", success=success, duration=duration, commands=commands)


def generate_summary(results: list[JobResult]) -> Table:
    """Generate summary table of job results.

    Args:
        results: List of JobResult instances

    Returns:
        Rich Table with summary

    """
    table = Table(title="Quality Check Summary", show_header=True, header_style="bold")

    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Duration", justify="right")
    table.add_column("Commands", justify="center")

    for job in results:
        status = "[green]✓ PASSED[/green]" if job.success else "[red]✗ FAILED[/red]"
        duration = f"{job.duration:.2f}s"
        total_commands = len(job.commands)
        successful_commands = sum(1 for cmd in job.commands if cmd.success)
        success_rate = f"{successful_commands}/{total_commands}"

        table.add_row(job.name.upper(), status, duration, success_rate)

    return table


def _generate_error_summary(failed_jobs: list[JobResult], total_duration: float, fix: bool) -> str:
    """Generate error summary message.

    Args:
        failed_jobs: List of failed jobs
        total_duration: Total execution duration
        fix: Whether auto-fix was enabled

    Returns:
        Formatted error summary string

    """
    error_summary = "[bold red]✗ Some checks failed[/bold red]\n\n"
    error_summary += "[yellow]Failed checks:[/yellow]\n"

    for job in failed_jobs:
        failed_commands = [cmd for cmd in job.commands if not cmd.success]
        error_summary += f"  • {job.name.upper()}: {len(failed_commands)} command(s) failed\n"

    error_summary += f"\n[dim]Total duration: {total_duration:.2f}s[/dim]\n\n"

    if fix:
        error_summary += (
            "[cyan]💡 Tip: Some issues were auto-fixed. Review changes before committing.[/cyan]"
        )
    else:
        error_summary += "[cyan]💡 Tip: Run with --fix to auto-fix some issues.[/cyan]"

    return error_summary


def check_command(
    project_root: Path,
    ruff: bool = True,
    pyright: bool = False,
    tests: bool = False,
    fix: bool = False,
) -> bool:
    """Run quality checks.

    Args:
        project_root: Project root directory
        ruff: Run Ruff checks
        pyright: Run Pyright checks
        tests: Run tests
        fix: Auto-fix issues where possible

    Returns:
        True if all checks passed, False otherwise

    """
    runner = WorkflowRunner(project_root)
    results: list[JobResult] = []

    # Run Ruff checks
    if ruff:
        result = run_ruff_check(runner, fix=fix)
        results.append(result)
        if not result.success:
            console.print("\n[red]Ruff checks failed.[/red]")

    # Run Pyright checks
    if pyright:
        result = run_pyright_check(runner)
        results.append(result)

        if not result.success:
            console.print("\n[yellow]Pyright checks failed (continuing...).[/yellow]")

    # Run tests
    if tests:
        result = run_tests(runner)
        results.append(result)
        if not result.success:
            console.print("\n[red]Tests failed.[/red]")

    # Generate summary
    if not results:
        return True

    console.print("\n" + "=" * 80 + "\n")
    console.print(generate_summary(results))

    total_duration = sum(job.duration for job in results)
    all_success = all(job.success for job in results)

    console.print("\n" + "=" * 80 + "\n")

    if all_success:
        console.print(
            Panel.fit(
                f"[bold green]✓ All checks passed![/bold green]\n"
                f"[dim]Total duration: {total_duration:.2f}s[/dim]",
                border_style="green",
            )
        )
        return True

    # Show summary of failed checks with suggestions
    failed_jobs = [job for job in results if not job.success]
    error_summary = _generate_error_summary(failed_jobs, total_duration, fix)
    console.print(Panel.fit(error_summary, border_style="red"))
    return False
