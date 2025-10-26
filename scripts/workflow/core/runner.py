"""Workflow command runner."""

import subprocess
import time
from pathlib import Path

from rich.console import Console

from .models import CommandResult, JobResult

console = Console()


class WorkflowRunner:
    """Runs workflow commands and tracks results."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: list[JobResult] = []

    def run_command(
        self, name: str, command: str, show_output: bool = True, check: bool = False
    ) -> CommandResult:
        """Run a command and return the result.

        Args:
            name: Display name for the command
            command: Shell command to execute
            show_output: Whether to show command output in real-time
            check: Whether to raise exception on failure

        Returns:
            CommandResult with execution details

        """
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

            if check and not success:
                msg = f"Command failed: {name}"
                raise RuntimeError(msg)

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

            if check:
                raise

            return CommandResult(
                name=name,
                command=command,
                success=False,
                duration=duration,
                output="",
                error=str(e),
            )
