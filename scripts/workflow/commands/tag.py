"""Tag management commands."""

from pathlib import Path

import typer

from ..infrastructure import execute_command, get_current_version
from ..presentation import RichConsole, create_table, render_command_execution
from ..types import CommandResult, ExecutionResult

console = RichConsole()


def _create_version_tag(
    project_root: Path,
    custom_version: str | None = None,
    push: bool = False,
    force: bool = False,
    skip_confirm: bool = False,
) -> tuple[bool, str]:
    """Create a version tag.

    Args:
        project_root: Project root directory
        custom_version: Custom version string (uses current version if not provided)
        push: Whether to push the tag after creation
        force: Force overwrite existing tag

    Returns:
        Tuple of (success, tag_name)

    """
    console.print_panel(
        "[bold magenta]Create Version Tag[/bold magenta]",
        subtitle="Create git tag for current version",
        style="magenta",
    )

    # Get current version
    try:
        current_version = get_current_version(project_root)
        console.print_success(f"Current version in pyproject.toml: {current_version}")
    except (FileNotFoundError, ValueError) as e:
        console.print_error(f"Error: {e}")
        return False, ""

    # Determine tag version
    if custom_version:
        tag_version = custom_version
        console.print(f"[cyan]Using custom version: {tag_version}[/cyan]")
    else:
        tag_version = current_version
        console.print(f"[cyan]Creating tag for current version: {tag_version}[/cyan]")

    tag_name = f"v{tag_version}"

    # Confirm tag creation
    if not skip_confirm:
        if not typer.confirm(f"\nCreate tag {tag_name}?"):
            console.print_warning("Tag creation cancelled.")
            return False, ""

    # Create tag (with force flag if requested)
    force_flag = "-f" if force else ""
    cmd = f'git tag {force_flag} -a {tag_name} -m "Release {tag_version}"'
    result = execute_command(cmd, cwd=project_root)
    render_command_execution(console, f"Create tag {tag_name}", cmd, result)

    if not result.success:
        console.print_error(f"\n✗ Failed to create tag {tag_name}")
        return False, tag_name

    console.print_success(f"\n✓ Tag {tag_name} created successfully!")

    # Push tag if requested
    if push:
        force_push = "--force" if force else ""
        push_cmd = f"git push {force_push} origin {tag_name}"
        push_result = execute_command(push_cmd, cwd=project_root)
        render_command_execution(console, f"Push tag {tag_name}", push_cmd, push_result)

        if push_result.success:
            console.print_success(f"✓ Tag {tag_name} pushed to remote!")
        else:
            console.print_error(f"✗ Failed to push tag {tag_name}")
            return False, tag_name

    return True, tag_name


def _list_tags(project_root: Path, limit: int = 10) -> bool:
    """List recent git tags.

    Args:
        project_root: Project root directory
        limit: Number of tags to show

    Returns:
        True if successful, False otherwise

    """
    console.print_panel(
        "[bold cyan]Recent Tags[/bold cyan]",
        subtitle=f"Last {limit} tags",
        style="cyan",
    )

    cmd = f"git tag --sort=-version:refname | head -n {limit}"
    result = execute_command(cmd, cwd=project_root, stream_output=True)
    render_command_execution(console, "List tags", cmd, result, show_output=True)

    return result.success


def _delete_tag(project_root: Path, tag_name: str, remote: bool = False) -> bool:
    """Delete a git tag.

    Args:
        project_root: Project root directory
        tag_name: Name of the tag to delete
        remote: Whether to also delete from remote

    Returns:
        True if successful, False otherwise

    """
    console.print_panel(
        "[bold red]Delete Tag[/bold red]",
        subtitle=f"Delete tag {tag_name}",
        style="red",
    )

    # Confirm deletion
    if not typer.confirm(f"Delete tag {tag_name}?"):
        console.print_warning("Tag deletion cancelled.")
        return False

    # Delete local tag
    cmd = f"git tag -d {tag_name}"
    result = execute_command(cmd, cwd=project_root)
    render_command_execution(console, f"Delete local tag {tag_name}", cmd, result)

    if not result.success:
        console.print_error(f"\n✗ Failed to delete tag {tag_name}")
        return False

    console.print_success(f"\n✓ Local tag {tag_name} deleted!")

    # Delete remote tag if requested
    if remote:
        if not typer.confirm(f"Also delete {tag_name} from remote?"):
            console.print_warning("Remote tag deletion cancelled.")
            return True

        remote_cmd = f"git push origin --delete {tag_name}"
        remote_result = execute_command(remote_cmd, cwd=project_root)
        render_command_execution(console, f"Delete remote tag {tag_name}", remote_cmd, remote_result)

        if remote_result.success:
            console.print_success(f"✓ Remote tag {tag_name} deleted!")
        else:
            console.print_error(f"✗ Failed to delete remote tag {tag_name}")
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
    skip_confirm: bool = False,
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
    if action == "create":
        success, _ = _create_version_tag(
            project_root,
            custom_version=custom_version,
            push=push,
            force=force,
            skip_confirm=skip_confirm,
        )
        return success

    if action == "list":
        return _list_tags(project_root, limit=limit)

    if action == "delete":
        if not tag_name:
            console.print_error("Error: tag_name is required for delete action")
            return False
        return _delete_tag(project_root, tag_name, remote=remote)

    console.print_error(f"Error: Unknown action '{action}'")
    return False
