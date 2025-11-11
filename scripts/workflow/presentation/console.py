"""Console interface - abstraction for console operations."""

from abc import ABC, abstractmethod

from rich.console import Console as RichConsoleType
from rich.panel import Panel
from rich.table import Table


class ConsoleInterface(ABC):
    """Abstract interface for console operations."""

    @abstractmethod
    def print(self, text: str) -> None:
        """Print text."""

    @abstractmethod
    def print_panel(self, title: str, subtitle: str = "", style: str = "blue") -> None:
        """Print a panel."""

    @abstractmethod
    def print_table(self, table: Table) -> None:
        """Print a table."""

    @abstractmethod
    def print_error(self, message: str) -> None:
        """Print error message."""

    @abstractmethod
    def print_success(self, message: str) -> None:
        """Print success message."""

    @abstractmethod
    def print_warning(self, message: str) -> None:
        """Print warning message."""


class RichConsole(ConsoleInterface):
    """Rich console implementation."""

    def __init__(self, console: RichConsoleType | None = None):
        """Initialize with optional Rich console.

        Args:
            console: Optional Rich Console instance (creates new if None)

        """
        self._console = console or RichConsoleType()

    def print(self, text: str) -> None:
        """Print text."""
        self._console.print(text)

    def print_panel(self, title: str, subtitle: str = "", style: str = "blue") -> None:
        """Print a panel."""
        panel = Panel.fit(title, subtitle=subtitle, border_style=style)
        self._console.print(panel)

    def print_table(self, table: Table) -> None:
        """Print a table."""
        self._console.print(table)

    def print_error(self, message: str) -> None:
        """Print error message."""
        self._console.print(f"[red]{message}[/red]")

    def print_success(self, message: str) -> None:
        """Print success message."""
        self._console.print(f"[green]{message}[/green]")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self._console.print(f"[yellow]{message}[/yellow]")


# Default console instance
console = RichConsole()
