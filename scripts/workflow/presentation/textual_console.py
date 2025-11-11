"""Textual console implementation."""

import queue
import threading
import time
from contextlib import contextmanager
from io import StringIO
from typing import ContextManager

from rich.console import Console as RichConsoleType
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from textual.app import App
from textual.widgets import RichLog, Static

from .console import ConsoleInterface


class TextualConsole(ConsoleInterface):
    """Textual implementation of ConsoleInterface."""

    def __init__(
        self, log_widget: RichLog, app: App | None = None, status_widget: Static | None = None
    ) -> None:
        """Initialize Textual console.

        Args:
            log_widget: Textual RichLog widget for output
            app: Textual App instance (for thread-safe updates)
            status_widget: Optional Static widget for showing status/spinner

        """
        self._log = log_widget
        self._app = app
        self._status_widget = status_widget
        # Queue for buffering writes from worker threads
        # Can contain strings or Rich renderables (Panel, Table, etc.)
        self._write_queue: queue.Queue[str | Panel | Table] = queue.Queue()
        self._processing = False
        
        # Get log widget width for proper rendering
        # Default to 100 if not available
        # Note: size may not be available during __init__, so we use a reasonable default
        log_width = 100
        try:
            if hasattr(log_widget, 'size') and log_widget.size.width > 0:
                log_width = log_widget.size.width
            elif hasattr(log_widget, 'content_size') and log_widget.content_size.width > 0:
                log_width = log_widget.content_size.width
        except Exception:
            pass
        
        # Create a Rich Console for rendering tables/panels to strings
        # Use StringIO to capture output (never write to real terminal)
        # Use log widget width minus padding to avoid horizontal scroll
        # Minimum width of 60 to ensure readability
        console_width = max(60, log_width - 4)
        self._rich_console = RichConsoleType(
            file=StringIO(), width=console_width, legacy_windows=False, force_terminal=False
        )
        
        # Start processing queue if we have an app
        if self._app:
            self._start_queue_processor()
    
    def __del__(self) -> None:
        """Cleanup when console is destroyed."""
        self._processing = False
    
    def _start_queue_processor(self) -> None:
        """Start processing the write queue."""
        if self._processing:
            return
        self._processing = True
        
        def process_queue() -> None:
            """Process queued writes with throttling."""
            batch = []
            last_flush = time.time()
            
            while self._processing:
                try:
                    # Get item with timeout
                    item = self._write_queue.get(timeout=0.1)
                    batch.append(item)
                    
                    # Flush batch every 50ms or when batch reaches 10 items
                    now = time.time()
                    if len(batch) >= 10 or (now - last_flush) >= 0.05:
                        self._flush_batch(batch)
                        batch = []
                        last_flush = now
                except queue.Empty:
                    # Flush any remaining items
                    if batch:
                        self._flush_batch(batch)
                        batch = []
                        last_flush = time.time()
        
        # Start processing in a daemon thread
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def _flush_batch(self, batch: list[str | Panel | Table]) -> None:
        """Flush a batch of writes to the RichLog widget."""
        if not batch or not self._app:
            return
        
        try:
            # Write each item separately (RichLog handles Rich renderables better this way)
            for content in batch:
                self._app.call_from_thread(self._log.write, content)
        except Exception:
            # Fallback: write directly if call_from_thread fails
            try:
                for content in batch:
                    self._log.write(content)
            except Exception:
                # Last resort: try to write as string
                for content in batch:
                    try:
                        if isinstance(content, str):
                            self._log.write(content)
                        else:
                            # For Rich renderables, try to convert to string
                            with self._rich_console.capture() as capture:
                                self._rich_console.print(content)
                            self._log.write(capture.get())
                    except Exception:
                        pass

    def _write_safe(self, content: str | Panel | Table) -> None:
        """Write content to RichLog widget in a thread-safe manner.

        Args:
            content: Text (str) or Rich renderable (Panel, Table, etc.) to write

        """
        if not content:
            return
            
        if self._app:
            # Check if we're in the main thread or a worker thread
            try:
                app_thread_id = getattr(self._app, "_thread_id", None)
                current_thread_id = threading.get_ident()
                
                # If we're in a different thread, queue the write
                if app_thread_id is not None and current_thread_id != app_thread_id:
                    self._write_queue.put(content)
                else:
                    # We're in the main thread, can write directly
                    self._log.write(content)
            except Exception:
                # Fallback: try to write directly
                try:
                    self._log.write(content)
                except Exception:
                    pass
        else:
            # No app, write directly
            try:
                self._log.write(content)
            except Exception:
                pass

    def print(self, text: str) -> None:
        """Print text to Textual log widget.

        Args:
            text: Text to print (supports Rich markup)

        """
        # Process text line by line to avoid overwhelming the UI
        # Split by newlines and write each line separately
        if not text:
            return
        
        lines = text.splitlines()
        for line in lines:
            if line.strip():  # Only write non-empty lines
                self._write_safe(line)
            else:
                # Write empty lines as well to preserve formatting
                self._write_safe("")

    def print_panel(self, title: str, subtitle: str = "", style: str = "blue") -> None:
        """Print a panel to Textual RichLog widget.

        Args:
            title: Panel title (supports Rich markup)
            subtitle: Panel subtitle (supports Rich markup)
            style: Border style

        """
        # RichLog supports Rich renderables, so we can use Panel directly
        panel = Panel.fit(title, subtitle=subtitle, border_style=style)
        self._write_safe(panel)  # RichLog.write() accepts Rich renderables

    def print_table(self, table: Table) -> None:
        """Print a table to Textual RichLog widget.

        Args:
            table: Rich Table instance

        """
        # RichLog supports Rich renderables, so we can use Table directly
        self._write_safe(table)  # RichLog.write() accepts Rich renderables

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Error message (supports Rich markup)

        """
        self._write_safe(f"[red]{message}[/red]")

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Success message (supports Rich markup)

        """
        self._write_safe(f"[green]{message}[/green]")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Warning message (supports Rich markup)

        """
        self._write_safe(f"[yellow]{message}[/yellow]")

    def task(self, description: str, spinner: str = "dots") -> ContextManager[None]:
        """Context manager for showing a task with spinner in RichLog.

        Args:
            description: Task description
            spinner: Spinner style (dots, line, moon, etc.)

        Returns:
            Context manager - use with 'with' statement

        Example:
            with console.task("Running checks..."):
                # Do work here
                pass
        """
        return self._task_impl(description, spinner)

    def _update_status(self, text: str) -> None:
        """Update status widget if available."""
        if self._status_widget and self._app:
            try:
                app_thread_id = getattr(self._app, "_thread_id", None)
                current_thread_id = threading.get_ident()
                
                if app_thread_id is not None and current_thread_id != app_thread_id:
                    self._app.call_from_thread(self._status_widget.update, text)
                else:
                    self._status_widget.update(text)
            except Exception:
                pass

    @contextmanager
    def _task_impl(self, description: str, spinner: str):  # noqa: ANN201, ARG002
        """Internal implementation of task context manager with spinner animation.
        
        Uses a Static widget for status updates if available, otherwise falls back to log messages.
        """
        spinner_sequence = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        _task_start = time.time()

        # Show initial status
        initial_msg = f"[cyan]▶ {description}[/cyan]"
        if self._status_widget:
            self._update_status(initial_msg)
        else:
            self._write_safe(initial_msg)

        # Start spinner animation if we have app and status widget
        if self._app and self._status_widget:
            _stop_spinner = threading.Event()

            def animate_spinner() -> None:
                """Animate spinner by updating status widget."""
                idx = 0
                last_update = time.time()
                update_interval = 0.15  # Update every 150ms for smooth animation

                while not _stop_spinner.is_set():
                    current_time = time.time()
                    elapsed = current_time - _task_start
                    
                    if current_time - last_update >= update_interval:
                        char = spinner_sequence[idx % len(spinner_sequence)]
                        elapsed_str = f" ({elapsed:.1f}s)" if elapsed >= 0.5 else ""
                        status_text = f"[cyan]{char}[/cyan] [cyan]{description}[/cyan]{elapsed_str}"
                        self._update_status(status_text)
                        idx += 1
                        last_update = current_time
                    
                    time.sleep(0.05)  # Check every 50ms

            spinner_thread = threading.Thread(target=animate_spinner, daemon=True)
            spinner_thread.start()

            try:
                yield
            finally:
                _stop_spinner.set()
                time.sleep(0.2)  # Small delay to ensure spinner stops
                # Show completion
                elapsed = time.time() - _task_start
                duration_str = f" ({elapsed:.2f}s)" if elapsed >= 0.1 else ""
                completion_msg = f"[green]✓[/green] [green]{description}[/green][dim]{duration_str}[/dim]"
                self._update_status(completion_msg)
                # Also log to RichLog
                self._write_safe(f"[green]✓[/green] {description}{duration_str}")
        else:
            # Fallback: just show start and end in log
            try:
                yield
            finally:
                elapsed = time.time() - _task_start
                duration_str = f" ({elapsed:.2f}s)" if elapsed >= 0.1 else ""
                self._write_safe(f"[green]✓[/green] {description}{duration_str}")

