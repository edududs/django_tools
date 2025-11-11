"""Push commands for git operations."""

from pathlib import Path

import typer

from ..domain.git_operations import should_push_commits, should_push_tags
from ..infrastructure import (
    count_commits_to_push,
    execute_command,
    get_current_branch,
    get_unpushed_tags,
    has_uncommitted_changes,
)
from ..presentation import RichConsole, render_command_execution

console = RichConsole()


def _push_commits(project_root: Path, force: bool = False, check_first: bool = True) -> bool:
    """Push commits to remote.

    Args:
        project_root: Project root directory
        force: Force push (use with caution)
        check_first: Check if there are commits to push first

    Returns:
        True if push succeeded, False otherwise

    """
    console.print_panel(
        "[bold blue]Push Commits[/bold blue]", subtitle="Push commits to remote", style="blue"
    )

    # Check if there are commits to push
    if check_first and not force:
        branch = get_current_branch()
        commits_count = count_commits_to_push(branch)

        if not should_push_commits(commits_count, force):
            console.print_warning("No commits to push. Branch is up to date.")
            return True

        console.print_success(f"Found {commits_count} commit(s) to push.")

    # Push commits
    push_cmd = "git push --force" if force else "git push"
    result = execute_command(push_cmd, cwd=project_root)
    render_command_execution(console, "Push commits", push_cmd, result)

    if result.success:
        console.print_success("\n✓ Commits pushed successfully!")
        return True
    console.print_error("\n✗ Failed to push commits")
    return False


def _push_tags(project_root: Path, check_first: bool = True) -> bool:
    """Push tags to remote.

    Args:
        project_root: Project root directory
        check_first: Check if there are tags to push first

    Returns:
        True if push succeeded, False otherwise

    """
    console.print_panel(
        "[bold cyan]Push Tags[/bold cyan]", subtitle="Push tags to remote", style="cyan"
    )

    # Check if there are tags to push
    if check_first:
        unpushed_tags = get_unpushed_tags()

        if not should_push_tags(len(unpushed_tags)):
            console.print_warning("No tags to push. All tags are up to date.")
            return True

        console.print_success(f"Found {len(unpushed_tags)} tag(s) to push:")
        for tag in unpushed_tags:
            console.print(f"  • {tag}")

    # Push tags
    result = execute_command("git push --tags", cwd=project_root)
    render_command_execution(console, "Push tags", "git push --tags", result)

    if result.success:
        console.print_success("\n✓ Tags pushed successfully!")
        return True
    console.print_error("\n✗ Failed to push tags")
    return False


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
    if force and not tags_only:
        console.print_warning("⚠ Warning: Force push enabled!")
        has_uncommitted = has_uncommitted_changes()
        if has_uncommitted:
            console.print_warning("Cannot force push with uncommitted changes.")
            return False

        if not typer.confirm("Are you sure you want to force push?"):
            console.print_warning("Push cancelled.")
            return False

    check_first = not skip_check

    if tags_only:
        return _push_tags(project_root, check_first=check_first)

    # Push commits first, then tags
    commits_success = _push_commits(project_root, force=force, check_first=check_first)
    tags_success = _push_tags(project_root, check_first=check_first)

    success = commits_success and tags_success

    if success:
        console.print_success("\n✓ All pushes completed successfully!")
    else:
        console.print_error("\n✗ Some pushes failed")

    return success
