"""Push commands for git operations."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from ..core import WorkflowRunner
from ..utils import count_commits_to_push, get_current_branch, get_unpushed_tags

console = Console()


def push_commits(
    runner: WorkflowRunner,
    force: bool = False,
    check_first: bool = True,
) -> bool:
    """Push commits to remote.

    Args:
        runner: WorkflowRunner instance
        force: Force push (use with caution)
        check_first: Check if there are commits to push first

    Returns:
        True if push succeeded, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold blue]Push Commits[/bold blue]",
            subtitle="Push commits to remote",
            border_style="blue",
        )
    )

    # Check if there are commits to push
    if check_first and not force:
        branch = get_current_branch()
        commits_to_push = count_commits_to_push(branch)

        if commits_to_push == 0:
            console.print("[yellow]No commits to push. Branch is up to date.[/yellow]")
            return True

        console.print(f"[green]Found {commits_to_push} commit(s) to push.[/green]")

    # Push commits
    push_cmd = "git push --force" if force else "git push"
    result = runner.run_command("Push commits", push_cmd)

    if result.success:
        console.print("\n[bold green]✓ Commits pushed successfully![/bold green]")
        return True
    console.print("\n[bold red]✗ Failed to push commits[/bold red]")
    return False


def push_tags_only(runner: WorkflowRunner, check_first: bool = True) -> bool:
    """Push tags to remote.

    Args:
        runner: WorkflowRunner instance
        check_first: Check if there are tags to push first

    Returns:
        True if push succeeded, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold cyan]Push Tags[/bold cyan]",
            subtitle="Push tags to remote",
            border_style="cyan",
        )
    )

    # Check if there are tags to push
    if check_first:
        unpushed_tags = get_unpushed_tags()

        if not unpushed_tags:
            console.print("[yellow]No tags to push. All tags are up to date.[/yellow]")
            return True

        console.print(f"[green]Found {len(unpushed_tags)} tag(s) to push:[/green]")
        for tag in unpushed_tags:
            console.print(f"  • {tag}")

    # Push tags
    result = runner.run_command("Push tags", "git push --tags")

    if result.success:
        console.print("\n[bold green]✓ Tags pushed successfully![/bold green]")
        return True
    console.print("\n[bold red]✗ Failed to push tags[/bold red]")
    return False


def push_all(
    runner: WorkflowRunner,
    force: bool = False,
    check_first: bool = True,
) -> bool:
    """Push both commits and tags to remote.

    Args:
        runner: WorkflowRunner instance
        force: Force push commits (use with caution)
        check_first: Check if there are commits/tags to push first

    Returns:
        True if all pushes succeeded, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold magenta]Push All[/bold magenta]",
            subtitle="Push commits and tags to remote",
            border_style="magenta",
        )
    )

    # Push commits first
    commits_success = push_commits(runner, force=force, check_first=check_first)

    # Push tags
    tags_success = push_tags_only(runner, check_first=check_first)

    success = commits_success and tags_success

    if success:
        console.print("\n[bold green]✓ All pushes completed successfully![/bold green]")
    else:
        console.print("\n[bold red]✗ Some pushes failed[/bold red]")

    return success


def push_command(
    project_root: Path,
    tags_only: bool = False,
    force: bool = False,
    skip_check: bool = False,
) -> bool:
    """Execute push command.

    Args:
        project_root: Project root directory
        tags_only: Push only tags, not commits
        force: Force push (use with caution)
        skip_check: Skip checking if there's anything to push

    Returns:
        True if push succeeded, False otherwise

    """
    runner = WorkflowRunner(project_root)

    if force and not tags_only:
        console.print("[yellow]⚠ Warning: Force push enabled![/yellow]")
        if not typer.confirm("Are you sure you want to force push?"):
            console.print("[yellow]Push cancelled.[/yellow]")
            return False

    check_first = not skip_check

    if tags_only:
        return push_tags_only(runner, check_first=check_first)
    return push_all(runner, force=force, check_first=check_first)
