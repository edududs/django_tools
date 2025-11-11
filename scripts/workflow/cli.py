"""CLI interface for workflow commands."""

from itertools import count
from pathlib import Path

import typer

from .commands import check_command, push_command, tag_command, version_command
from .domain.project import find_project_root, find_target_path, validate_project_root
from .infrastructure import ConfigManager
from .presentation import RichConsole, render_config
from .types import TagAction
from .utils.constants import SEPARATOR_WIDTH

app = typer.Typer(
    name="workflow",
    help="Workflow automation for code quality and releases",
    add_completion=False,
)
console = RichConsole()

# Default config file path
DEFAULT_CONFIG_FILE = Path.home() / ".workflow_config.json"
_config_manager = ConfigManager(DEFAULT_CONFIG_FILE)


def _get_project_root(path: str | None = None, use_config: bool = True) -> Path:
    """Get project root directory.

    Args:
        path: Optional custom project root path
        use_config: Whether to use configured environment root

    Returns:
        Project root path

    Raises:
        typer.Exit: If pyproject.toml not found

    """
    # If explicit path provided, validate it
    if path:
        project_root = Path(path)
        if not validate_project_root(project_root):
            console.print_error(f"Error: pyproject.toml not found in {project_root}")
            raise typer.Exit(1)
        return project_root

    # Check for configured environment root
    if use_config:
        env_root = _config_manager.get_env_root()
        if env_root and validate_project_root(env_root):
            return env_root

    # Default behavior: search from current directory
    project_root = find_project_root()
    if not project_root:
        console.print_error("Error: pyproject.toml not found. Are you in the project root?")
        console.print_warning("Tip: Use 'workflow config set-env' to configure an environment.")
        raise typer.Exit(1)

    return project_root


def _run_validation(
    project_root: Path,
    ruff: bool = True,
    pyright: bool = False,
    tests: bool = False,
    fix: bool = False,
) -> bool:
    """Run validation checks.

    Args:
        project_root: Project root directory
        ruff: Run Ruff checks
        pyright: Run Pyright checks
        tests: Run tests
        fix: Auto-fix issues

    Returns:
        True if validation passed, False otherwise

    """
    console.print("\n[bold cyan]Running validation...[/bold cyan]\n")

    target_path = _get_target_path(use_config=True)
    success = check_command(
        project_root,
        ruff=ruff,
        pyright=pyright,
        tests=tests,
        fix=fix,
        target_path=target_path,
    )

    if not success:
        console.print_error("\nValidation failed.")
        console.print_warning("Use --no-validate to skip validation (not recommended)")
        return False

    console.print_success("\n✓ Validation passed!\n")
    return True


def _get_target_path(target: str | None = None, use_config: bool = True) -> Path | None:
    """Get target path for validation.

    Args:
        target: Optional custom target path
        use_config: Whether to use configured target path

    Returns:
        Target path or None

    Raises:
        typer.Exit: If target path doesn't exist

    """
    if target:
        target_path = Path(target)
        if not target_path.exists():
            console.print_error(f"Error: Directory {target_path} does not exist")
            raise typer.Exit(1)
        return target_path

    # Check for configured target path
    if use_config:
        config = _config_manager.load()
        return find_target_path(config)

    return None


@app.command()
def check(
    path: str = typer.Option(None, "--path", help="Project root directory"),
    ruff: bool = typer.Option(True, "--ruff/--no-ruff", help="Run Ruff checks"),
    pyright: bool = typer.Option(False, "--pyright/--no-pyright", help="Run Pyright checks"),
    tests: bool = typer.Option(False, "--tests/--no-tests", help="Run tests"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues where possible"),
):
    """Run quality checks (ruff, pyright, tests).

    By default, only runs Ruff checks. Use flags to enable other checks.
    """
    console.print_panel(
        "[bold green]Quality Checks[/bold green]",
        subtitle="Verify code",
        style="green",
    )

    project_root = _get_project_root(path)
    target_path = _get_target_path(use_config=True)
    success = check_command(
        project_root,
        ruff=ruff,
        pyright=pyright,
        tests=tests,
        fix=fix,
        target_path=target_path,
    )

    if not success:
        raise typer.Exit(1)


@app.command()
def full(
    path: str = typer.Option(None, "--path", help="Project root directory"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues where possible"),
    skip_pyright: bool = typer.Option(False, "--skip-pyright", help="Skip Pyright checks"),
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip tests"),
):
    """Run all quality checks (ruff + pyright + tests).

    This is the comprehensive check before pushing code.
    """
    console.print_panel(
        "[bold magenta]Full Quality Check[/bold magenta]",
        subtitle="Complete validation suite",
        style="magenta",
    )

    project_root = _get_project_root(path)
    target_path = _get_target_path(use_config=True)
    success = check_command(
        project_root,
        ruff=True,
        pyright=not skip_pyright,
        tests=not skip_tests,
        fix=fix,
        target_path=target_path,
    )

    if not success:
        raise typer.Exit(1)


@app.command()
def push(
    path: str = typer.Option(None, "--path", help="Project root directory"),
    tags_only: bool = typer.Option(False, "--tags-only", help="Push only tags, not commits"),
    force: bool = typer.Option(False, "--force", help="Force push (use with caution)"),
    skip_check: bool = typer.Option(
        False, "--skip-check", help="Skip checking if there's anything to push"
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", help="Run quality checks before push"
    ),
):
    """Push commits and/or tags to remote.

    By default, runs quality checks before pushing.
    Use --no-validate to skip validation (not recommended).
    """
    project_root = _get_project_root(path)

    # Run validation if requested
    if (
        validate
        and not force
        and not _run_validation(project_root, ruff=True, pyright=False, tests=False, fix=False)
    ):
        raise typer.Exit(1)

    # Execute push
    success = push_command(
        project_root,
        tags_only=tags_only,
        force=force,
        skip_check=skip_check,
    )

    if not success:
        raise typer.Exit(1)


@app.command()
def release(
    path: str = typer.Option(None, "--path", help="Project root directory"),
    push_after: bool = typer.Option(False, "--push", help="Push tag after creation"),
    force: bool = typer.Option(False, "--force", help="Force overwrite existing tag"),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", help="Run full validation before release"
    ),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues before validation"),
    push_commits: bool = typer.Option(
        False, "--push-commits", help="Push commits before creating tag"
    ),
):
    """Create release tag and optionally push.

    This command:
    1. Optionally auto-fixes issues (--fix)
    2. Runs full validation (ruff + pyright + tests)
    3. Optionally pushes commits (--push-commits)
    4. Creates a tag for the current version in pyproject.toml
    5. Optionally pushes the tag to remote (--push)

    Note: You must manually update the version in pyproject.toml first!
    """
    console.print_panel(
        "[bold magenta]Release Process[/bold magenta]",
        subtitle="Create and push release tag",
        style="magenta",
    )

    project_root = _get_project_root(path)
    target_path = _get_target_path(use_config=True)

    step_counter = count(1)

    # Step 1: Auto-fix if requested
    if fix:
        step_num = next(step_counter)
        console.print(f"\n[bold cyan]Step {step_num}: Auto-fixing issues...[/bold cyan]\n")
        fix_success = check_command(
            project_root,
            ruff=True,
            pyright=False,
            tests=False,
            fix=True,
            target_path=target_path,
        )

        if not fix_success:
            console.print_warning("\n⚠ Some issues could not be auto-fixed. Continuing...\n")

    # Step 2: Run full validation if requested
    if validate:
        step_num = next(step_counter)
        console.print(f"\n[bold cyan]Step {step_num}: Running full validation...[/bold cyan]\n")
        if not _run_validation(project_root, ruff=True, pyright=True, tests=True):
            raise typer.Exit(1)

    # Step 3: Push commits if requested
    if push_commits:
        step_num = next(step_counter)
        console.print(f"\n[bold cyan]Step {step_num}: Pushing commits...[/bold cyan]\n")
        push_success = push_command(
            project_root,
            tags_only=False,
            force=False,
            skip_check=False,
        )

        if not push_success:
            console.print_error("\nPush failed. Release aborted.")
            raise typer.Exit(1)

        console.print_success("\n✓ Commits pushed successfully!\n")

    # Step 4: Create tag
    step_num = next(step_counter)
    console.print(f"\n[bold cyan]Step {step_num}: Creating release tag...[/bold cyan]\n")
    success = tag_command(
        project_root,
        action=TagAction.CREATE,
        push=push_after,
        force=force,
        skip_confirm=True,  # Auto-confirm in release workflow
    )

    if not success:
        raise typer.Exit(1)

    # Final message
    console.print(f"\n{'=' * SEPARATOR_WIDTH}\n")
    success_msg = (
        "[bold green]✓ Release completed successfully![/bold green]\n"
        "[dim]Tag created and ready for deployment.[/dim]"
    )
    console.print_panel(success_msg, style="green")


@app.command()
def tag(
    action: str = typer.Argument("list", help="Action: create, list, delete"),
    path: str = typer.Option(None, "--path", help="Project root directory"),
    tag_name: str = typer.Option(None, "--name", help="Tag name (for delete action)"),
    push_after: bool = typer.Option(False, "--push", help="Push tag after creation"),
    force: bool = typer.Option(
        False, "--force", help="Force overwrite existing tag (create action)"
    ),
    remote: bool = typer.Option(False, "--remote", help="Also delete from remote (delete action)"),
    limit: int = typer.Option(10, "--limit", help="Number of tags to show (list action)"),
):
    """Manage git tags.

    Actions:
    - create: Create a tag for current version in pyproject.toml
    - list: List recent tags
    - delete: Delete a tag
    """
    project_root = _get_project_root(path)

    success = tag_command(
        project_root,
        action=action,
        push=push_after,
        force=force,
        tag_name=tag_name,
        remote=remote,
        limit=limit,
    )

    if not success:
        raise typer.Exit(1)


@app.command()
def version(
    path: str = typer.Option(None, "--path", help="Project root directory"),
):
    """Show current version and calculate next versions."""
    project_root = _get_project_root(path)

    success = version_command(project_root)

    if not success:
        raise typer.Exit(1)


@app.command()
def deploy(
    path: str = typer.Option(None, "--path", help="Project root directory"),
    skip_validation: bool = typer.Option(False, "--skip-validation", help="Skip validation checks"),
):
    """Complete deployment workflow: validate + push commits + push tags.

    This is the recommended way to deploy code to production.
    It runs all checks and pushes everything in one command.
    """
    console.print_panel(
        "[bold yellow]🚀 Deployment Workflow[/bold yellow]",
        subtitle="Complete validation and push",
        style="yellow",
    )

    project_root = _get_project_root(path)

    # Step 1: Full validation
    if not skip_validation:
        console.print("\n[bold cyan]Step 1/3: Running full validation...[/bold cyan]\n")
        if not _run_validation(project_root, ruff=True, pyright=True, tests=True):
            raise typer.Exit(1)
    else:
        console.print_warning("\n⚠ Skipping validation (not recommended)\n")

    # Step 2: Push commits
    console.print("\n[bold cyan]Step 2/3: Pushing commits...[/bold cyan]\n")
    push_success = push_command(
        project_root,
        tags_only=False,
        force=False,
        skip_check=False,
    )

    if not push_success:
        console.print_error("\nPush failed. Deployment aborted.")
        raise typer.Exit(1)

    # Final message
    console.print(f"\n{'=' * SEPARATOR_WIDTH}\n")
    success_msg = (
        "[bold green]✓ Deployment completed successfully![/bold green]\n"
        "[dim]All changes have been validated and pushed to remote.[/dim]"
    )
    console.print_panel(success_msg, style="green")


@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, set-env, set-target, clear"),
    path: str = typer.Option(None, "--path", help="Path to set (for set-env/set-target actions)"),
):
    """Manage workflow configuration.

    Actions:
    - show: Display current configuration
    - set-env: Set environment root (where pyproject.toml is)
    - set-target: Set target path for validation
    - clear: Clear all configuration
    """
    if action == "show":
        config = _config_manager.load()
        render_config(console, config, DEFAULT_CONFIG_FILE)

    elif action == "set-env":
        if not path:
            console.print_error("Error: --path is required for set-env action")
            console.print_warning("Example: workflow config set-env --path /path/to/project")
            raise typer.Exit(1)

        env_root = Path(path)
        if not validate_project_root(env_root):
            console.print_error(f"Error: pyproject.toml not found in {env_root}")
            raise typer.Exit(1)

        _config_manager.set_env_root(env_root)
        console.print_success(f"✓ Environment root set to: {env_root}")
        console.print(
            "\n[dim]All workflow commands will now use this environment's configuration.[/dim]"
        )

    elif action == "set-target":
        if not path:
            console.print_error("Error: --path is required for set-target action")
            console.print_warning("Example: workflow config set-target --path /path/to/validate")
            raise typer.Exit(1)

        target_path = Path(path)
        if not target_path.exists():
            console.print_error(f"Error: Directory {target_path} does not exist")
            raise typer.Exit(1)

        _config_manager.set_target_path(target_path)
        console.print_success(f"✓ Target path set to: {target_path}")
        console.print("\n[dim]Validation will be performed on this directory.[/dim]")

    elif action == "clear":
        _config_manager.clear()
        console.print_success("✓ Configuration cleared")

    else:
        console.print_error(f"Error: Unknown action '{action}'")
        console.print_warning("Valid actions: show, set-env, set-target, clear")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
