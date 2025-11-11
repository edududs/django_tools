"""Formatters - pure formatting functions."""

from rich.panel import Panel
from rich.table import Table


def format_command_name(name: str) -> str:
    """Format command name for display.

    Args:
        name: Command name

    Returns:
        Formatted command name

    """
    return f"[bold cyan]▶ {name}[/bold cyan]"


def format_command_line(command: str) -> str:
    """Format command line for display.

    Args:
        command: Command line

    Returns:
        Formatted command line

    """
    return f"[dim]$ {command}[/dim]"


def format_duration(seconds: float) -> str:
    """Format duration for display.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string

    """
    return f"[dim]({seconds:.2f}s)[/dim]"


def format_status(success: bool) -> str:
    """Format status for display.

    Args:
        success: Whether operation succeeded

    Returns:
        Formatted status string

    """
    return "[green]✓[/green]" if success else "[red]✗[/red]"


def create_panel(title: str, subtitle: str = "", style: str = "blue") -> Panel:
    """Create a Rich panel.

    Args:
        title: Panel title
        subtitle: Panel subtitle
        style: Border style

    Returns:
        Panel instance

    """
    return Panel.fit(title, subtitle=subtitle, border_style=style)


def create_table(headers: list[str]) -> Table:
    """Create a Rich table.

    Args:
        headers: Table headers

    Returns:
        Table instance

    """
    table = Table()
    for header in headers:
        table.add_column(header)
    return table

