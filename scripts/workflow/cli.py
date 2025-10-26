"""CLI interface for workflow commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .commands import check_command, push_command, tag_command, version_command
from .config import workflow_config

app = typer.Typer(
    name="workflow",
    help="Workflow automation for code quality and releases",
    add_completion=False,
)
console = Console()


def get_project_root(path: str | None = None, use_config: bool = True) -> Path:
    """Get project root directory (environment root).

    Args:
        path: Optional custom project root path
        use_config: Whether to use configured environment root

    Returns:
        Project root path (where pyproject.toml is)

    Raises:
        typer.Exit: If pyproject.toml not found

    """
    if path:
        project_root = Path(path)
        if not project_root.exists():
            console.print(f"[red]Error: Directory {project_root} does not exist[/red]")
            raise typer.Exit(1)
        if not (project_root / "pyproject.toml").exists():
            console.print(f"[red]Error: pyproject.toml not found in {project_root}[/red]")
            raise typer.Exit(1)
        return project_root

    # Check for configured environment root
    if use_config:
        env_root = workflow_config.get_env_root()
        if env_root and env_root.exists() and (env_root / "pyproject.toml").exists():
            return env_root

    # Default behavior
    project_root = Path(__file__).parent.parent.parent
    if not (project_root / "pyproject.toml").exists():
        console.print("[red]Error: pyproject.toml not found. Are you in the project root?[/red]")
        console.print(
            "[yellow]Tip: Use 'workflow config set-env' to configure an environment.[/yellow]"
        )
        raise typer.Exit(1)
    return project_root


def get_target_path(target: str | None = None, use_config: bool = True) -> Path | None:
    """Get target path for validation.

    Args:
        target: Optional custom target path
        use_config: Whether to use configured target path

    Returns:
        Target path or None (means use env_root)

    """
    if target:
        target_path = Path(target)
        if not target_path.exists():
            console.print(f"[red]Error: Directory {target_path} does not exist[/red]")
            raise typer.Exit(1)
        return target_path

    # Check for configured target path
    if use_config:
        return workflow_config.get_target_path()

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
    console.print(
        Panel.fit(
            "[bold green]Quality Checks[/bold green]",
            subtitle="Verify code",
            border_style="green",
        )
    )

    project_root = get_project_root(path)
    success = check_command(
        project_root,
        ruff=ruff,
        pyright=pyright,
        tests=tests,
        fix=fix,
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
    console.print(
        Panel.fit(
            "[bold magenta]Full Quality Check[/bold magenta]",
            subtitle="Complete validation suite",
            border_style="magenta",
        )
    )

    project_root = get_project_root(path)
    success = check_command(
        project_root,
        ruff=True,
        pyright=not skip_pyright,
        tests=not skip_tests,
        fix=fix,
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
    project_root = get_project_root(path)

    # Run validation if requested
    if validate and not force:
        console.print("\n[bold cyan]Running validation before push...[/bold cyan]\n")
        validation_success = check_command(
            project_root,
            ruff=True,
            pyright=False,
            tests=False,
            fix=False,
        )

        if not validation_success:
            console.print("\n[bold red]Validation failed. Push aborted.[/bold red]")
            console.print("[yellow]Use --no-validate to skip validation (not recommended)[/yellow]")
            raise typer.Exit(1)

        console.print("\n[bold green]✓ Validation passed![/bold green]\n")

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
):
    """Create release tag and optionally push.

    This command:
    1. Runs full validation (ruff + pyright + tests)
    2. Creates a tag for the current version in pyproject.toml
    3. Optionally pushes the tag to remote

    Note: You must manually update the version in pyproject.toml first!
    """
    console.print(
        Panel.fit(
            "[bold magenta]Release Process[/bold magenta]",
            subtitle="Create and push release tag",
            border_style="magenta",
        )
    )

    project_root = get_project_root(path)

    # Run full validation if requested
    if validate:
        console.print("\n[bold cyan]Running full validation...[/bold cyan]\n")
        validation_success = check_command(
            project_root,
            ruff=True,
            pyright=True,
            tests=True,
            fix=False,
        )

        if not validation_success:
            console.print("\n[bold red]Validation failed. Release aborted.[/bold red]")
            raise typer.Exit(1)

        console.print("\n[bold green]✓ Validation passed![/bold green]\n")

    # Create tag
    success = tag_command(
        project_root,
        action="create",
        push=push_after,
        force=force,
    )

    if not success:
        raise typer.Exit(1)


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
    project_root = get_project_root(path)

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
    project_root = get_project_root(path)

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
    console.print(
        Panel.fit(
            "[bold yellow]🚀 Deployment Workflow[/bold yellow]",
            subtitle="Complete validation and push",
            border_style="yellow",
        )
    )

    project_root = get_project_root(path)

    # Step 1: Full validation
    if not skip_validation:
        console.print("\n[bold cyan]Step 1/3: Running full validation...[/bold cyan]\n")
        validation_success = check_command(
            project_root,
            ruff=True,
            pyright=True,
            tests=True,
            fix=False,
        )

        if not validation_success:
            console.print("\n[bold red]Validation failed. Deployment aborted.[/bold red]")
            raise typer.Exit(1)

        console.print("\n[bold green]✓ Validation passed![/bold green]\n")
    else:
        console.print("\n[yellow]⚠ Skipping validation (not recommended)[/yellow]\n")

    # Step 2: Push commits
    console.print("\n[bold cyan]Step 2/3: Pushing commits...[/bold cyan]\n")
    push_success = push_command(
        project_root,
        tags_only=False,
        force=False,
        skip_check=False,
    )

    if not push_success:
        console.print("\n[bold red]Push failed. Deployment aborted.[/bold red]")
        raise typer.Exit(1)

    # Final message
    console.print("\n" + "=" * 80 + "\n")
    console.print(
        Panel.fit(
            "[bold green]✓ Deployment completed successfully![/bold green]\n"
            "[dim]All changes have been validated and pushed to remote.[/dim]",
            border_style="green",
        )
    )


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
        workflow_config.show_config()

    elif action == "set-env":
        if not path:
            console.print("[red]Error: --path is required for set-env action[/red]")
            console.print(
                "[yellow]Example: workflow config set-env --path /path/to/project[/yellow]"
            )
            raise typer.Exit(1)

        env_root = Path(path)
        if not env_root.exists():
            console.print(f"[red]Error: Directory {env_root} does not exist[/red]")
            raise typer.Exit(1)

        if not (env_root / "pyproject.toml").exists():
            console.print(f"[red]Error: pyproject.toml not found in {env_root}[/red]")
            raise typer.Exit(1)

        workflow_config.set_env_root(env_root)
        console.print(f"[green]✓ Environment root set to: {env_root}[/green]")
        console.print(
            "\n[dim]All workflow commands will now use this environment's configuration.[/dim]"
        )

    elif action == "set-target":
        if not path:
            console.print("[red]Error: --path is required for set-target action[/red]")
            console.print(
                "[yellow]Example: workflow config set-target --path /path/to/validate[/yellow]"
            )
            raise typer.Exit(1)

        target_path = Path(path)
        if not target_path.exists():
            console.print(f"[red]Error: Directory {target_path} does not exist[/red]")
            raise typer.Exit(1)

        workflow_config.set_target_path(target_path)
        console.print(f"[green]✓ Target path set to: {target_path}[/green]")
        console.print("\n[dim]Validation will be performed on this directory.[/dim]")

    elif action == "clear":
        workflow_config.clear_env_root()
        workflow_config.clear_target_path()
        console.print("[green]✓ Configuration cleared[/green]")

    else:
        console.print(f"[red]Error: Unknown action '{action}'[/red]")
        console.print("[yellow]Valid actions: show, set-env, set-target, clear[/yellow]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
