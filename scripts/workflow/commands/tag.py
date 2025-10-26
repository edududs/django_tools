"""Tag management commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from ..core import WorkflowRunner
from ..utils import get_current_version

console = Console()


def create_version_tag(
    runner: WorkflowRunner,
    project_root: Path,
    custom_version: str | None = None,
    push: bool = False,
    force: bool = False,
) -> tuple[bool, str]:
    """Create a version tag.

    Args:
        runner: WorkflowRunner instance
        project_root: Project root directory
        custom_version: Custom version string (uses current version if not provided)
        push: Whether to push the tag after creation
        force: Force overwrite existing tag

    Returns:
        Tuple of (success, tag_name)

    """
    console.print(
        Panel.fit(
            "[bold magenta]Create Version Tag[/bold magenta]",
            subtitle="Create git tag for current version",
            border_style="magenta",
        )
    )

    # Get current version
    try:
        current_version = get_current_version(project_root)
        console.print(f"[green]Current version in pyproject.toml: {current_version}[/green]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error: {e}[/red]")
        return False, ""

    # Determine tag version
    if custom_version:
        tag_version = custom_version
        console.print(f"[cyan]Using custom version: {tag_version}[/cyan]")
    else:
        # Use current version from pyproject.toml (already bumped manually)
        tag_version = current_version
        console.print(f"[cyan]Creating tag for current version: {tag_version}[/cyan]")

    tag_name = f"v{tag_version}"

    # Confirm tag creation
    if not typer.confirm(f"\nCreate tag {tag_name}?"):
        console.print("[yellow]Tag creation cancelled.[/yellow]")
        return False, ""

    # Create tag (with force flag if requested)
    force_flag = "-f" if force else ""
    result = runner.run_command(
        f"Create tag {tag_name}",
        f'git tag {force_flag} -a {tag_name} -m "Release {tag_version}"',
    )

    if not result.success:
        console.print(f"\n[bold red]✗ Failed to create tag {tag_name}[/bold red]")
        return False, tag_name

    console.print(f"\n[bold green]✓ Tag {tag_name} created successfully![/bold green]")

    # Push tag if requested
    if push:
        force_push = "--force" if force else ""
        push_result = runner.run_command(
            f"Push tag {tag_name}",
            f"git push {force_push} origin {tag_name}",
        )

        if push_result.success:
            console.print(f"[bold green]✓ Tag {tag_name} pushed to remote![/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to push tag {tag_name}[/bold red]")
            return False, tag_name

    return True, tag_name


def list_tags(runner: WorkflowRunner, limit: int = 10) -> bool:
    """List recent git tags.

    Args:
        runner: WorkflowRunner instance
        limit: Number of tags to show

    Returns:
        True if successful, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold cyan]Recent Tags[/bold cyan]",
            subtitle=f"Last {limit} tags",
            border_style="cyan",
        )
    )

    result = runner.run_command(
        "List tags",
        f"git tag --sort=-version:refname | head -n {limit}",
        show_output=True,
    )

    return result.success


def delete_tag(
    runner: WorkflowRunner,
    tag_name: str,
    remote: bool = False,
) -> bool:
    """Delete a git tag.

    Args:
        runner: WorkflowRunner instance
        tag_name: Name of the tag to delete
        remote: Whether to also delete from remote

    Returns:
        True if successful, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold red]Delete Tag[/bold red]",
            subtitle=f"Delete tag {tag_name}",
            border_style="red",
        )
    )

    # Confirm deletion
    if not typer.confirm(f"Delete tag {tag_name}?"):
        console.print("[yellow]Tag deletion cancelled.[/yellow]")
        return False

    # Delete local tag
    result = runner.run_command(
        f"Delete local tag {tag_name}",
        f"git tag -d {tag_name}",
    )

    if not result.success:
        console.print(f"\n[bold red]✗ Failed to delete tag {tag_name}[/bold red]")
        return False

    console.print(f"\n[bold green]✓ Local tag {tag_name} deleted![/bold green]")

    # Delete remote tag if requested
    if remote:
        if not typer.confirm(f"Also delete {tag_name} from remote?"):
            console.print("[yellow]Remote tag deletion cancelled.[/yellow]")
            return True

        remote_result = runner.run_command(
            f"Delete remote tag {tag_name}",
            f"git push origin --delete {tag_name}",
        )

        if remote_result.success:
            console.print(f"[bold green]✓ Remote tag {tag_name} deleted![/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to delete remote tag {tag_name}[/bold red]")
            return False

    return True


def tag_command(
    project_root: Path,
    action: str = "create",
    custom_version: str | None = None,
    push: bool = False,
    force: bool = False,
    tag_name: str | None = None,
    remote: bool = False,
    limit: int = 10,
) -> bool:
    """Execute tag command.

    Args:
        project_root: Project root directory
        action: Action to perform ("create", "list", "delete")
        custom_version: Custom version for create action
        push: Whether to push tag after creation
        force: Force overwrite existing tag (create action)
        tag_name: Tag name for delete action
        remote: Whether to delete from remote (delete action)
        limit: Number of tags to show (list action)

    Returns:
        True if successful, False otherwise

    """
    runner = WorkflowRunner(project_root)

    if action == "create":
        success, _ = create_version_tag(
            runner,
            project_root,
            custom_version=custom_version,
            push=push,
            force=force,
        )
        return success

    if action == "list":
        return list_tags(runner, limit=limit)

    if action == "delete":
        if not tag_name:
            console.print("[red]Error: tag_name is required for delete action[/red]")
            return False
        return delete_tag(runner, tag_name, remote=remote)

    console.print(f"[red]Error: Unknown action '{action}'[/red]")
    return False
