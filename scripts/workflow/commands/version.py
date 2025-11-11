"""Version management commands."""

from pathlib import Path

from ..domain.version import calculate_next_version
from ..infrastructure import get_current_version
from ..presentation import RichConsole, create_panel, create_table

console = RichConsole()


def version_command(project_root: Path) -> bool:
    """Show current version and calculate next versions.

    Args:
        project_root: Project root directory

    Returns:
        True if successful, False otherwise

    """
    console.print_panel(
        "[bold cyan]Version Information[/bold cyan]",
        subtitle="Current and next versions",
        style="cyan",
    )

    try:
        current_version = get_current_version(project_root)
    except (FileNotFoundError, ValueError) as e:
        console.print_error(f"Error: {e}")
        return False

    # Calculate next versions
    try:
        next_patch = calculate_next_version(current_version, "patch")
        next_minor = calculate_next_version(current_version, "minor")
        next_major = calculate_next_version(current_version, "major")
    except ValueError as e:
        console.print_error(f"Error calculating versions: {e}")
        return False

    # Create table
    table = create_table(["Type", "Version"])
    table.title = "Version Information"
    table.show_header = True
    table.header_style = "bold cyan"

    table.add_row("Current", current_version)
    table.add_row("Next Patch", next_patch)
    table.add_row("Next Minor", next_minor)
    table.add_row("Next Major", next_major)

    console.print_table(table)

    return True
