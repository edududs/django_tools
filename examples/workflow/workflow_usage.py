"""Workflow Usage Examples.

This module demonstrates how to use the workflow system directly,
showing the complete command execution flow.

Key Concepts:
- Direct function calls: No complex DI, just import and call
- WorkflowRunner: Execute shell commands with tracking
- Command layer: High-level commands (check, push, tag, version)
- Utils: Pure functions for Git operations
- Configuration: Persistent settings management
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from scripts.workflow.config import workflow_config
from scripts.workflow.core import CommandResult, WorkflowRunner
from scripts.workflow.utils import (
    count_commits_to_push,
    get_current_branch,
    get_current_version,
    get_unpushed_tags,
)

app = typer.Typer()
console = Console()


def demonstrate_project_root():
    """Show how to get project root."""
    console.print(Panel.fit("📁 Project Root", style="bold cyan"))

    # Default: Current working directory
    project_root = Path.cwd()

    # Or use configured environment root
    env_root = workflow_config.get_env_root()
    if env_root:
        console.print(f"[green]Using configured env root:[/green] {env_root}")
        project_root = env_root

    console.print(f"[cyan]Project root:[/cyan] {project_root}")
    console.print(f"[cyan]Has pyproject.toml:[/cyan] {(project_root / 'pyproject.toml').exists()}")

    return project_root


def demonstrate_workflow_runner(project_root: Path):
    """Demonstrate WorkflowRunner for executing commands."""
    console.print("\n")
    console.print(Panel.fit("⚙️ WorkflowRunner", style="bold magenta"))

    runner = WorkflowRunner(project_root)

    console.print("\n[bold]1. Execute a single command:[/bold]")
    result: CommandResult = runner.run_command(
        "Check Python version",
        "python --version",
        show_output=True,
    )

    console.print(f"   [green]✓[/green] Success: {result.success}")
    console.print(f"   [green]✓[/green] Duration: {result.duration:.2f}s")

    console.print("\n[bold]2. Track multiple commands:[/bold]")
    commands = [
        runner.run_command("List files", "ls -la", show_output=False),
        runner.run_command("Check git status", "git status", show_output=False),
    ]

    success_rate = sum(1 for cmd in commands if cmd.success) / len(commands) * 100
    console.print(f"   [green]✓[/green] Success rate: {success_rate:.0f}%")

    console.print("\n[dim]→ WorkflowRunner tracks all command execution details[/dim]")
    console.print("[dim]→ Returns CommandResult with success, duration, output, error[/dim]")


def demonstrate_commands(project_root: Path):  # noqa: ARG001
    """Demonstrate workflow commands."""
    console.print("\n")
    console.print(Panel.fit("🎯 Workflow Commands", style="bold blue"))

    console.print("\n[bold]1. Version Command:[/bold]")
    console.print("[dim]Shows current version and calculates next versions[/dim]")
    tree = Tree("version_command(project_root)")
    tree.add("[green]Returns:[/green] bool (success)")

    console.print(tree)

    console.print("\n[bold]2. Check Command:[/bold]")
    console.print("[dim]Runs quality checks (Ruff, Pyright, Fab tests)[/dim]")
    tree = Tree("check_command(project_root, ruff=True, pyright=False, tests=False, fix=False)")
    tree.add("[green]Returns:[/green] bool (all checks passed)")

    console.print(tree)

    console.print("\n[bold]3. Tag Command:[/bold]")
    console.print("[dim]Manages git tags (create, list, delete)[/dim]")
    tree = Tree("tag_command(project_root, action='list', limit=10)")
    tree.add("[green]Returns:[/green] bool (success)")

    console.print(tree)

    console.print("\n[bold]4. Push Command:[/bold]")
    console.print("[dim]Pushes commits and tags to remote[/dim]")
    tree = Tree("push_command(project_root, tags_only=False, force=False)")
    tree.add("[green]Returns:[/green] bool (push succeeded)")

    console.print(tree)

    console.print("\n[dim]→ All commands accept project_root as first argument[/dim]")
    console.print("[dim]→ Commands return simple bool for success/failure[/dim]")


def demonstrate_git_utils(project_root: Path):
    """Demonstrate Git utility functions."""
    console.print("\n")
    console.print(Panel.fit("🔧 Git Utilities", style="bold yellow"))

    console.print("\n[bold]Available utilities:[/bold]")

    # Get current version
    try:
        version = get_current_version(project_root)
        console.print(f"   [green]✓[/green] Current version: [cyan]{version}[/cyan]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"   [red]✗[/red] Could not get version: {e}")

    # Get current branch
    try:
        branch = get_current_branch()
        console.print(f"   [green]✓[/green] Current branch: [cyan]{branch}[/cyan]")
    except RuntimeError as e:
        console.print(f"   [red]✗[/red] Could not get branch: {e}")

    # Count commits to push
    try:
        commits = count_commits_to_push()
        console.print(f"   [green]✓[/green] Commits to push: [cyan]{commits}[/cyan]")
    except RuntimeError as e:
        console.print(f"   [red]✗[/red] Could not count commits: {e}")

    # Get unpushed tags
    try:
        unpushed = get_unpushed_tags()
        console.print(f"   [green]✓[/green] Unpushed tags: [cyan]{len(unpushed)}[/cyan]")
        if unpushed:
            for tag in unpushed[:5]:  # Show first 5
                console.print(f"      • [dim]{tag}[/dim]")
    except RuntimeError as e:
        console.print(f"[red]✗[/red] Could not get unpushed tags: {e}")

    console.print("\n[dim]→ All utilities are pure functions (no side effects)[/dim]")
    console.print("[dim]→ Easy to test and mock in tests[/dim]")


def demonstrate_configuration():
    """Demonstrate configuration management."""
    console.print("\n")
    console.print(Panel.fit("⚙️ Configuration Management", style="bold green"))

    console.print("\n[bold]Current configuration:[/bold]")

    config = workflow_config.get_config()
    if config:
        for key, value in config.items():
            console.print(f"   [green]{key}:[/green] {value}")
    else:
        console.print("   [dim]No configuration set[/dim]")

    console.print("\n[dim]→ Configuration stored in:[/dim] ~/.workflow_config.json")
    console.print("[dim]→ Supports env_root and target_path settings[/dim]")
    console.print("[dim]→ Use 'workflow config set-env' to configure[/dim]")


def demonstrate_command_execution(project_root: Path):  # noqa: ARG001
    """Demonstrate executing a real command."""
    console.print("\n")
    console.print(Panel.fit("🚀 Command Execution Example", style="bold magenta"))

    console.print("\n[bold]Example: Running version command[/bold]")
    console.print("[dim]This would show current version and next versions[/dim]\n")

    # Note: We don't actually run it to avoid cluttering output
    console.print("[yellow]# version_command(project_root)[/yellow]")
    console.print("[dim]# Would display version information...[/dim]\n")

    console.print("[green]✓[/green] Commands follow consistent patterns:")
    console.print("  • Accept project_root as first argument")
    console.print("  • Return bool for success/failure")
    console.print("  • Handle errors internally and display messages")
    console.print("  • Can be used directly or via CLI")


def run_all_examples():
    """Run all workflow examples."""
    console.print(Panel.fit("📚 Workflow Usage Examples", style="bold"))

    project_root = demonstrate_project_root()
    demonstrate_workflow_runner(project_root)
    demonstrate_commands(project_root)
    demonstrate_git_utils(project_root)
    demonstrate_configuration()
    demonstrate_command_execution(project_root)

    console.print("\n")
    console.print(Panel.fit("📋 Summary", style="bold green"))

    summary = Tree("Workflow Architecture Benefits")
    summary.add("[green]✓[/green] Simple: Direct function calls, no complex DI")
    summary.add("[green]✓[/green] Testable: Functions accept parameters")
    summary.add("[green]✓[/green] Type-safe: Full type hints throughout")
    summary.add("[green]✓[/green] Flexible: Use CLI or call directly")
    summary.add("[green]✓[/green] Clear: Separate layers (CLI, commands, core, utils)")

    console.print(summary)

    console.print("\n[bold]Entry Points:[/bold]")
    console.print("  • CLI: [cyan]uv run python -m scripts.workflow.cli <command>[/cyan]")
    console.print("  • Direct: [cyan]from scripts.workflow.commands import check_command[/cyan]")
    console.print("  • Make: [cyan]make check[/cyan] or [cyan]make full[/cyan]")


if __name__ == "__main__":
    run_all_examples()
