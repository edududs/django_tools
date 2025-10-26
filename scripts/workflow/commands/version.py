"""Version management commands."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..utils import calculate_next_version, get_current_version

console = Console()


def show_version_info(project_root: Path) -> bool:
    """Show current version and calculate next versions.

    Args:
        project_root: Project root directory

    Returns:
        True if successful, False otherwise

    """
    console.print(
        Panel.fit(
            "[bold cyan]Version Information[/bold cyan]",
            subtitle="Current and next versions",
            border_style="cyan",
        )
    )

    try:
        current_version = get_current_version(project_root)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

    # Calculate next versions
    try:
        next_patch = calculate_next_version(current_version, "patch")
        next_minor = calculate_next_version(current_version, "minor")
        next_major = calculate_next_version(current_version, "major")
    except ValueError as e:
        console.print(f"[red]Error calculating versions: {e}[/red]")
        return False

    # Create table
    table = Table(title="Version Information", show_header=True, header_style="bold cyan")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")

    table.add_row("Current", current_version)
    table.add_row("Next Patch", next_patch)
    table.add_row("Next Minor", next_minor)
    table.add_row("Next Major", next_major)

    console.print(table)

    return True


def version_command(project_root: Path) -> bool:
    """Execute version command.

    Args:
        project_root: Project root directory

    Returns:
        True if successful, False otherwise

    """
    return show_version_info(project_root)
