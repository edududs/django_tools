#!/usr/bin/env python3
"""Workflow Dry Run Script.

Simulates the CI/CD workflow locally to ensure everything works correctly
on GitHub Actions. Uses Rich for visualization and Typer for CLI.
"""

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="workflow-dryrun",
    help="Simulate the CI/CD workflow locally",
    add_completion=False,
)
console = Console()


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


class WorkflowRunner:
    """Runs workflow jobs locally."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: list[JobResult] = []

    def run_command(self, name: str, command: str, show_output: bool = True) -> CommandResult:
        """Run a command and return the result."""
        start_time = time.time()

        console.print(f"\n[bold cyan]▶ {name}[/bold cyan]")
        console.print(f"[dim]$ {command}[/dim]")

        try:
            result = subprocess.run(  # noqa: S602
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=not show_output,
                text=True,
                check=False,
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            if not show_output:
                if result.stdout:
                    console.print(result.stdout)
                if result.stderr:
                    console.print(f"[yellow]{result.stderr}[/yellow]")

            status = "[green]✓[/green]" if success else "[red]✗[/red]"
            console.print(f"{status} {name} [dim]({duration:.2f}s)[/dim]")

            return CommandResult(
                name=name,
                command=command,
                success=success,
                duration=duration,
                output=result.stdout or "",
                error=result.stderr or "",
            )

        except Exception as e:
            duration = time.time() - start_time
            console.print(f"[red]✗ {name} - Error: {e}[/red]")
            return CommandResult(
                name=name,
                command=command,
                success=False,
                duration=duration,
                output="",
                error=str(e),
            )

    def run_test_job(self) -> JobResult:
        """Run the test job."""
        console.print(Panel.fit("[bold blue]Job: Test[/bold blue]", border_style="blue"))

        start_time = time.time()

        # Execute test job commands
        commands = [
            self.run_command("Verify Ruff installation", "uv run ruff --version"),
            self.run_command("Run Ruff linting and auto-fix", "uv run ruff check src/ --fix"),
            self.run_command("Run Ruff format", "uv run ruff format src/"),
            self.run_command(
                "Run tests with coverage",
                "uv run pytest src/ -v --cov=src --cov-report=term-missing",
            ),
        ]

        duration = time.time() - start_time
        success = all(cmd.success for cmd in commands)

        return JobResult(name="test", success=success, duration=duration, commands=commands)

    def run_release_job(self, dry_run: bool = True) -> JobResult:
        """Run the release job (simulated)."""
        console.print(
            Panel.fit("[bold magenta]Job: Release (Dry Run)[/bold magenta]", border_style="magenta")
        )

        start_time = time.time()

        # Get current version
        result = self.run_command(
            "Get current version",
            "grep '^version = ' pyproject.toml | sed 's/version = \"\\(.*\\)\"/\\1/'",
            show_output=False,
        )
        commands = [result]

        if result.success:
            current_version = result.output.strip()
            console.print(f"[green]Current version: {current_version}[/green]")

            # Calculate new version
            version_parts = current_version.split(".")
            if len(version_parts) == 3:
                major, minor, patch = version_parts
                new_patch = int(patch) + 1
                new_version = f"{major}.{minor}.{new_patch}"
                console.print(f"[green]New version would be: {new_version}[/green]")

                if not dry_run:
                    # Update pyproject.toml and create tag
                    commands.extend([
                        self.run_command(
                            "Update pyproject.toml",
                            f'sed -i "s/^version = \\".*\\"/version = \\"{new_version}\\"/" pyproject.toml',
                        ),
                        self.run_command("Create tag", f"git tag v{new_version}"),
                    ])
                else:
                    console.print("[yellow]Skipping version update (dry run)[/yellow]")

        # Build the package
        commands.append(self.run_command("Build package", "uv build"))

        duration = time.time() - start_time
        success = all(cmd.success for cmd in commands)

        return JobResult(name="release", success=success, duration=duration, commands=commands)

    def generate_summary(self) -> Table:
        """Generate a summary table of the job results."""
        table = Table(title="Workflow Execution Summary", show_header=True, header_style="bold")

        table.add_column("Job", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Duration", justify="right")
        table.add_column("Commands", justify="center")
        table.add_column("Success Rate", justify="center")

        for job in self.results:
            status = "[green]✓ PASSED[/green]" if job.success else "[red]✗ FAILED[/red]"
            duration = f"{job.duration:.2f}s"
            total_commands = len(job.commands)
            successful_commands = sum(1 for cmd in job.commands if cmd.success)
            success_rate = f"{successful_commands}/{total_commands}"

            table.add_row(job.name.upper(), status, duration, success_rate, "")

        return table

    def generate_detailed_report(self) -> Table:
        """Generate a detailed report of all commands."""
        table = Table(
            title="Detailed Command Report", show_header=True, header_style="bold magenta"
        )

        table.add_column("Job", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Duration", justify="right")

        for job in self.results:
            for i, cmd in enumerate(job.commands):
                status = "[green]✓[/green]" if cmd.success else "[red]✗[/red]"
                duration = f"{cmd.duration:.2f}s"

                job_name = job.name.upper() if i == 0 else ""
                table.add_row(job_name, cmd.name, status, duration)

        return table


@app.command()
def run(
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip test job"),
    skip_release: bool = typer.Option(False, "--skip-release", help="Skip release job"),
    no_dry_run: bool = typer.Option(
        False, "--no-dry-run", help="Actually perform version bump and tagging"
    ),
):
    """Run the full CI/CD workflow locally.

    By default, all jobs are executed in dry-run mode (no real changes performed).
    """
    console.print(
        Panel.fit(
            "[bold green]Workflow Dry Run - CI/CD Simulation[/bold green]",
            subtitle="Simulating GitHub Actions locally",
            border_style="green",
        )
    )

    project_root = Path(__file__).parent.parent
    runner = WorkflowRunner(project_root)

    # Check if we are in the correct directory
    if not (project_root / "pyproject.toml").exists():
        console.print("[red]Error: pyproject.toml not found. Are you in the project root?[/red]")
        raise typer.Exit(1)

    console.print(f"\n[dim]Project root: {project_root}[/dim]\n")

    # Run test job
    if not skip_tests:
        test_result = runner.run_test_job()
        runner.results.append(test_result)

        if not test_result.success:
            console.print("\n[red]Test job failed. Stopping workflow.[/red]")
            console.print(runner.generate_summary())
            raise typer.Exit(1)

    # Run release job
    if not skip_release:
        release_result = runner.run_release_job(dry_run=not no_dry_run)
        runner.results.append(release_result)

    # Generate reports
    console.print("\n" + "=" * 80 + "\n")
    console.print(runner.generate_summary())
    console.print("\n")
    console.print(runner.generate_detailed_report())

    # Final summary
    total_duration = sum(job.duration for job in runner.results)
    all_success = all(job.success for job in runner.results)

    console.print("\n" + "=" * 80 + "\n")

    if all_success:
        console.print(
            Panel.fit(
                f"[bold green]✓ All jobs completed successfully![/bold green]\n"
                f"[dim]Total duration: {total_duration:.2f}s[/dim]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold red]✗ Some jobs failed[/bold red]\n"
                f"[dim]Total duration: {total_duration:.2f}s[/dim]",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def check():
    """Run only quick checks (linting and formatting)."""
    console.print(
        Panel.fit(
            "[bold cyan]Quick Check - Linting & Formatting[/bold cyan]",
            border_style="cyan",
        )
    )

    project_root = Path(__file__).parent.parent
    runner = WorkflowRunner(project_root)

    commands = [
        runner.run_command("Ruff check", "uv run ruff check src/"),
        runner.run_command("Ruff format check", "uv run ruff format --check src/"),
    ]

    all_success = all(cmd.success for cmd in commands)

    if all_success:
        console.print("\n[bold green]✓ All checks passed![/bold green]")
    else:
        console.print("\n[bold red]✗ Some checks failed[/bold red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show current version and calculate next version."""
    project_root = Path(__file__).parent.parent
    pyproject = project_root / "pyproject.toml"

    if not pyproject.exists():
        console.print("[red]Error: pyproject.toml not found[/red]")
        raise typer.Exit(1)

    content = pyproject.read_text()
    match = re.search(r'version = "([^"]+)"', content)

    if match:
        current_version = match.group(1)
        version_parts = current_version.split(".")

        if len(version_parts) == 3:
            major, minor, patch = version_parts
            next_patch = f"{major}.{minor}.{int(patch) + 1}"
            next_minor = f"{major}.{int(minor) + 1}.0"
            next_major = f"{int(major) + 1}.0.0"

            table = Table(title="Version Information", show_header=True)
            table.add_column("Type", style="cyan")
            table.add_column("Version", style="green")

            table.add_row("Current", current_version)
            table.add_row("Next Patch", next_patch)
            table.add_row("Next Minor", next_minor)
            table.add_row("Next Major", next_major)

            console.print(table)
        else:
            console.print(f"[yellow]Current version: {current_version}[/yellow]")
    else:
        console.print("[red]Could not find version in pyproject.toml[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
