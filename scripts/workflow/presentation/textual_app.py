"""Textual TUI application."""

import threading
import time
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header, RichLog, Static, Tabs

from ..commands import check_command, push_command, tag_command, version_command
from ..domain.project import find_project_root
from ..infrastructure import ConfigManager
from ..types import TagAction
from .textual_console import TextualConsole

# Default config file path
DEFAULT_CONFIG_FILE = Path.home() / ".workflow_config.json"


class CheckScreen(Container):
    """Screen for quality checks."""

    DEFAULT_CSS = """
    CheckScreen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold cyan]Quality Checks[/bold cyan]", id="title")
        yield Static("", id="check-status")
        with Container(id="log-container"):
            yield RichLog(id="check-output", markup=True, wrap=True)
        with Horizontal(id="check-buttons"):
            yield Button("Run Ruff", id="ruff-btn", variant="primary")
            yield Button("Run Pyright", id="pyright-btn", variant="primary")
            yield Button("Run Tests", id="tests-btn", variant="primary")
            yield Button("Run All", id="all-btn", variant="success")
            yield Button("Fix Issues", id="fix-btn", variant="warning")


class PushScreen(Container):
    """Screen for git push operations."""

    DEFAULT_CSS = """
    PushScreen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold blue]Push Operations[/bold blue]", id="title")
        yield Static("", id="push-status")
        with Container(id="log-container"):
            yield RichLog(id="push-output", markup=True, wrap=True)
        with Horizontal(id="push-buttons"):
            yield Button("Push Commits", id="push-commits-btn", variant="primary")
            yield Button("Push Tags", id="push-tags-btn", variant="primary")
            yield Button("Push All", id="push-all-btn", variant="success")
            yield Button("Force Push", id="force-push-btn", variant="error")


class TagScreen(Container):
    """Screen for tag management."""

    DEFAULT_CSS = """
    TagScreen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold magenta]Tag Management[/bold magenta]", id="title")
        yield Static("", id="tag-status")
        with Container(id="log-container"):
            yield RichLog(id="tag-output", markup=True, wrap=True)
        with Horizontal(id="tag-buttons"):
            yield Button("Create Tag", id="create-tag-btn", variant="primary")
            yield Button("List Tags", id="list-tags-btn", variant="primary")
            yield Button("Delete Tag", id="delete-tag-btn", variant="error")


class VersionScreen(Container):
    """Screen for version information."""

    DEFAULT_CSS = """
    VersionScreen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold cyan]Version Information[/bold cyan]", id="title")
        yield Static("", id="version-status")
        with Container(id="log-container"):
            yield RichLog(id="version-output", markup=True, wrap=True)
        with Horizontal(id="version-buttons"):
            yield Button("Show Version", id="show-version-btn", variant="primary")


class ConfigScreen(Container):
    """Screen for configuration management."""

    DEFAULT_CSS = """
    ConfigScreen {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold yellow]Configuration[/bold yellow]", id="title")
        yield Static("", id="config-status")
        with Container(id="log-container"):
            yield RichLog(id="config-output", markup=True, wrap=True)
        with Horizontal(id="config-buttons"):
            yield Button("Show Config", id="show-config-btn", variant="primary")


class WorkflowApp(App):
    """Main Textual application for workflow."""

    CSS_PATH = "workflow.tcss"
    TITLE = "Workflow TUI"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("1", "switch_tab(0)", "Check"),
        ("2", "switch_tab(1)", "Push"),
        ("3", "switch_tab(2)", "Tag"),
        ("4", "switch_tab(3)", "Version"),
        ("5", "switch_tab(4)", "Config"),
        ("tab", "next_tab", "Next Tab"),
        ("shift+tab", "prev_tab", "Prev Tab"),
    ]

    def __init__(self) -> None:
        """Initialize the app."""
        super().__init__()
        self.project_root: Path | None = None
        self.config_manager = ConfigManager(DEFAULT_CONFIG_FILE)
        self._consoles: dict[str, TextualConsole] = {}
        self._button_labels: dict[str, str] = {}  # Store original button labels
        self._button_spinners: dict[str, threading.Thread] = {}  # Track spinner threads

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header(show_clock=True)
        with Container(id="app-container"):
            yield Tabs("Check", "Push", "Tag", "Version", "Config", id="main-tabs")
            with Container(id="screen-container"):
                yield CheckScreen(id="check-screen")
                yield PushScreen(id="push-screen")
                yield TagScreen(id="tag-screen")
                yield VersionScreen(id="version-screen")
                yield ConfigScreen(id="config-screen")
        yield Footer()

    def _update_screen_from_tabs(self) -> None:
        """Update visible screen based on active tab."""
        tabs_widget = self.query_one("#main-tabs", Tabs)
        active_tab_id = tabs_widget.active

        # Map tab IDs to screen names
        # Tabs are created with labels, so active should be the label
        screen_map = {
            "Check": "check",
            "Push": "push",
            "Tag": "tag",
            "Version": "version",
            "Config": "config",
        }

        screen_name = screen_map.get(active_tab_id or "Check", "check")
        self._show_screen(screen_name)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation - navigate to corresponding screen."""
        # Map tab labels to screen names
        screen_map = {
            "Check": "check",
            "Push": "push",
            "Tag": "tag",
            "Version": "version",
            "Config": "config",
        }

        # Get tab label - try different ways to access it
        tab_label = "Check"  # default
        try:
            if hasattr(event.tab, "label"):
                if hasattr(event.tab.label, "plain"):
                    tab_label = event.tab.label.plain
                else:
                    tab_label = str(event.tab.label)
        except Exception:
            # Fallback: use active tab from widget
            tabs_widget = self.query_one("#main-tabs", Tabs)
            tab_label = tabs_widget.active or "Check"

        screen_name = screen_map.get(tab_label, "check")
        self._show_screen(screen_name)

    def on_mount(self) -> None:
        """Initialize app on mount."""
        # Find project root
        self.project_root = find_project_root()
        if not self.project_root:
            # Try to get from config
            config = self.config_manager.load()
            if config.env_root:
                env_root = Path(config.env_root)
                if env_root.exists() and (env_root / "pyproject.toml").exists():
                    self.project_root = env_root

        # Initialize consoles for each screen
        check_log = self.query_one("#check-output", RichLog)
        check_status = self.query_one("#check-status", Static)
        push_log = self.query_one("#push-output", RichLog)
        push_status = self.query_one("#push-status", Static)
        tag_log = self.query_one("#tag-output", RichLog)
        tag_status = self.query_one("#tag-status", Static)
        version_log = self.query_one("#version-output", RichLog)
        version_status = self.query_one("#version-status", Static)
        config_log = self.query_one("#config-output", RichLog)
        config_status = self.query_one("#config-status", Static)

        self._consoles["check"] = TextualConsole(check_log, app=self, status_widget=check_status)
        self._consoles["push"] = TextualConsole(push_log, app=self, status_widget=push_status)
        self._consoles["tag"] = TextualConsole(tag_log, app=self, status_widget=tag_status)
        self._consoles["version"] = TextualConsole(
            version_log, app=self, status_widget=version_status
        )
        self._consoles["config"] = TextualConsole(config_log, app=self, status_widget=config_status)

        # Show initial message
        if self.project_root:
            self._consoles["check"].print_success(f"Project root: {self.project_root}")
        else:
            self._consoles["check"].print_error(
                "Project root not found. Please configure it in the Config tab."
            )

        # Store original button labels
        self._store_button_labels()

        # Show check screen by default and set up tab watching
        self._show_screen("check")
        # Watch for tab changes
        tabs_widget = self.query_one("#main-tabs", Tabs)
        self.watch(tabs_widget, "active", self._update_screen_from_tabs)

    def _store_button_labels(self) -> None:
        """Store original button labels for restoration."""
        button_ids = [
            "ruff-btn",
            "pyright-btn",
            "tests-btn",
            "all-btn",
            "fix-btn",
            "push-commits-btn",
            "push-tags-btn",
            "push-all-btn",
            "force-push-btn",
            "create-tag-btn",
            "list-tags-btn",
            "show-version-btn",
            "show-config-btn",
        ]
        for button_id in button_ids:
            try:
                button = self.query_one(f"#{button_id}", Button)
                label = button.label
                # Handle both string labels and Rich Text labels
                if isinstance(label, str):
                    self._button_labels[button_id] = label
                elif hasattr(label, "plain"):
                    self._button_labels[button_id] = label.plain  # type: ignore[attr-defined]
                else:
                    self._button_labels[button_id] = str(label)
            except Exception:
                pass

    def _set_button_loading(self, button_id: str, loading: bool) -> None:
        """Set button loading state (disable and show animated spinner).

        Thread-safe method that works from worker threads.

        Args:
            button_id: Button ID
            loading: True to show loading, False to restore normal state

        """
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

        def update_button_label(spinner_char: str = "") -> None:
            """Update button label with optional spinner character."""
            try:
                button = self.query_one(f"#{button_id}", Button)
                if loading:
                    # Store original label if not already stored
                    if button_id not in self._button_labels:
                        label = button.label
                        # Handle both string labels and Rich Text labels
                        if isinstance(label, str):
                            self._button_labels[button_id] = label
                        elif hasattr(label, "plain"):
                            self._button_labels[button_id] = label.plain  # type: ignore[attr-defined]
                        else:
                            self._button_labels[button_id] = str(label)
                    # Update label with spinner
                    original_label = self._button_labels.get(button_id, "")
                    char = spinner_char or "⠋"
                    button.label = f"{char} {original_label}"
                    button.disabled = True
                else:
                    # Restore original label
                    original_label = self._button_labels.get(button_id, "")
                    if original_label:
                        button.label = original_label
                    button.disabled = False
            except Exception:
                pass

        def animate_spinner() -> None:
            """Animate spinner in button label."""
            idx = 0
            last_update = time.time()
            update_interval = 0.15  # Update every 150ms

            while button_id in self._button_spinners:
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    char = spinner_chars[idx % len(spinner_chars)]
                    # Update button label with animated spinner
                    if app_thread_id := getattr(self, "_thread_id", None):
                        current_thread_id = threading.get_ident()
                        if current_thread_id != app_thread_id:
                            self.call_from_thread(update_button_label, char)
                        else:
                            update_button_label(char)
                    else:
                        update_button_label(char)
                    idx += 1
                    last_update = current_time
                time.sleep(0.05)  # Check every 50ms

        # Check if we're in the main thread
        try:
            app_thread_id = getattr(self, "_thread_id", None)
            current_thread_id = threading.get_ident()

            if loading:
                # Stop any existing spinner for this button
                if button_id in self._button_spinners:
                    del self._button_spinners[button_id]
                    time.sleep(0.1)  # Give thread time to stop

                # Start initial spinner state
                if app_thread_id is not None and current_thread_id != app_thread_id:
                    self.call_from_thread(update_button_label, "⠋")
                else:
                    update_button_label("⠋")

                # Start spinner animation thread
                spinner_thread = threading.Thread(target=animate_spinner, daemon=True)
                self._button_spinners[button_id] = spinner_thread
                spinner_thread.start()
            else:
                # Stop spinner thread
                if button_id in self._button_spinners:
                    del self._button_spinners[button_id]
                    time.sleep(0.1)  # Give thread time to stop

                # Restore button
                if app_thread_id is not None and current_thread_id != app_thread_id:
                    self.call_from_thread(update_button_label)
                else:
                    update_button_label()
        except Exception:
            # Fallback: try direct update
            update_button_label()

    def action_switch_tab(self, tab_index: int) -> None:
        """Switch to a specific tab by index."""
        tabs_widget = self.query_one("#main-tabs", Tabs)
        tab_labels = ["Check", "Push", "Tag", "Version", "Config"]
        if 0 <= tab_index < len(tab_labels):
            tabs_widget.active = tab_labels[tab_index]

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        tabs_widget = self.query_one("#main-tabs", Tabs)
        tab_labels = ["Check", "Push", "Tag", "Version", "Config"]
        current_label = tabs_widget.active or "Check"
        try:
            current_index = tab_labels.index(current_label)
            next_index = (current_index + 1) % len(tab_labels)
            tabs_widget.active = tab_labels[next_index]
        except ValueError:
            tabs_widget.active = "Check"

    def action_prev_tab(self) -> None:
        """Switch to previous tab."""
        tabs_widget = self.query_one("#main-tabs", Tabs)
        tab_labels = ["Check", "Push", "Tag", "Version", "Config"]
        current_label = tabs_widget.active or "Check"
        try:
            current_index = tab_labels.index(current_label)
            prev_index = (current_index - 1) % len(tab_labels)
            tabs_widget.active = tab_labels[prev_index]
        except ValueError:
            tabs_widget.active = "Check"

    def _show_screen(self, screen_name: str) -> None:
        """Show a specific screen."""
        screens = {
            "check": "check-screen",
            "push": "push-screen",
            "tag": "tag-screen",
            "version": "version-screen",
            "config": "config-screen",
        }
        screen_id = screens.get(screen_name, "check-screen")

        # Hide all screens
        for sid in screens.values():
            try:
                widget = self.query_one(f"#{sid}")
                widget.display = False
            except Exception:
                pass

        # Show selected screen
        try:
            widget = self.query_one(f"#{screen_id}")
            widget.display = True
        except Exception:
            pass

    # Check screen actions
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if not self.project_root:
            self._consoles["check"].print_error("Project root not found!")
            return

        if button_id == "ruff-btn":
            self.run_ruff_check()
        elif button_id == "pyright-btn":
            self.run_pyright_check()
        elif button_id == "tests-btn":
            self.run_tests_check()
        elif button_id == "all-btn":
            self.run_all_checks()
        elif button_id == "fix-btn":
            self.run_fix_issues()
        elif button_id == "push-commits-btn":
            self.run_push_commits()
        elif button_id == "push-tags-btn":
            self.run_push_tags()
        elif button_id == "push-all-btn":
            self.run_push_all()
        elif button_id == "force-push-btn":
            self.run_force_push()
        elif button_id == "create-tag-btn":
            self.run_create_tag()
        elif button_id == "list-tags-btn":
            self.run_list_tags()
        elif button_id == "delete-tag-btn":
            self.run_delete_tag()
        elif button_id == "show-version-btn":
            self.run_show_version()
        elif button_id == "show-config-btn":
            self.run_show_config()

    @work(thread=True)
    def run_ruff_check(self) -> None:
        """Run Ruff check."""
        self._set_button_loading("ruff-btn", True)
        try:
            console = self._consoles["check"]
            if self.project_root:
                with console.task("Running Ruff checks...", spinner="dots"):
                    check_command(
                        self.project_root, console=console, ruff=True, pyright=False, tests=False
                    )
        finally:
            self._set_button_loading("ruff-btn", False)

    @work(thread=True)
    def run_pyright_check(self) -> None:
        """Run Pyright check."""
        self._set_button_loading("pyright-btn", True)
        try:
            console = self._consoles["check"]
            if self.project_root:
                with console.task("Running Pyright type checking...", spinner="dots"):
                    check_command(
                        self.project_root, console=console, ruff=False, pyright=True, tests=False
                    )
        finally:
            self._set_button_loading("pyright-btn", False)

    @work(thread=True)
    def run_tests_check(self) -> None:
        """Run tests check."""
        self._set_button_loading("tests-btn", True)
        try:
            console = self._consoles["check"]
            if self.project_root:
                with console.task("Running tests...", spinner="dots"):
                    check_command(
                        self.project_root, console=console, ruff=False, pyright=False, tests=True
                    )
        finally:
            self._set_button_loading("tests-btn", False)

    @work(thread=True)
    def run_all_checks(self) -> None:
        """Run all checks."""
        self._set_button_loading("all-btn", True)
        try:
            console = self._consoles["check"]
            if self.project_root:
                with console.task("Running all checks...", spinner="dots"):
                    check_command(
                        self.project_root, console=console, ruff=True, pyright=True, tests=True
                    )
        finally:
            self._set_button_loading("all-btn", False)

    @work(thread=True)
    def run_fix_issues(self) -> None:
        """Run fix issues."""
        self._set_button_loading("fix-btn", True)
        try:
            console = self._consoles["check"]
            if self.project_root:
                with console.task("Fixing issues...", spinner="dots"):
                    check_command(
                        self.project_root,
                        console=console,
                        ruff=True,
                        pyright=False,
                        tests=False,
                        fix=True,
                    )
        finally:
            self._set_button_loading("fix-btn", False)

    @work(thread=True)
    def run_push_commits(self) -> None:
        """Run push commits."""
        self._set_button_loading("push-commits-btn", True)
        try:
            console = self._consoles["push"]
            if self.project_root:
                with console.task("Pushing commits...", spinner="dots"):
                    push_command(self.project_root, console=console, tags_only=False, force=False)
        finally:
            self._set_button_loading("push-commits-btn", False)

    @work(thread=True)
    def run_push_tags(self) -> None:
        """Run push tags."""
        self._set_button_loading("push-tags-btn", True)
        try:
            console = self._consoles["push"]
            if self.project_root:
                with console.task("Pushing tags...", spinner="dots"):
                    push_command(self.project_root, console=console, tags_only=True, force=False)
        finally:
            self._set_button_loading("push-tags-btn", False)

    @work(thread=True)
    def run_push_all(self) -> None:
        """Run push all."""
        self._set_button_loading("push-all-btn", True)
        try:
            console = self._consoles["push"]
            if self.project_root:
                with console.task("Pushing commits and tags...", spinner="dots"):
                    push_command(self.project_root, console=console, tags_only=False, force=False)
        finally:
            self._set_button_loading("push-all-btn", False)

    @work(thread=True)
    def run_force_push(self) -> None:
        """Run force push."""
        self._set_button_loading("force-push-btn", True)
        try:
            console = self._consoles["push"]
            if self.project_root:
                with console.task("Force pushing...", spinner="dots"):
                    push_command(self.project_root, console=console, tags_only=False, force=True)
        finally:
            self._set_button_loading("force-push-btn", False)

    @work(thread=True)
    def run_create_tag(self) -> None:
        """Run create tag."""
        self._set_button_loading("create-tag-btn", True)
        try:
            console = self._consoles["tag"]
            if self.project_root:
                with console.task("Creating tag...", spinner="dots"):
                    tag_command(
                        self.project_root,
                        console=console,
                        action=TagAction.CREATE,
                        skip_confirm=True,
                    )
        finally:
            self._set_button_loading("create-tag-btn", False)

    @work(thread=True)
    def run_list_tags(self) -> None:
        """Run list tags."""
        self._set_button_loading("list-tags-btn", True)
        try:
            console = self._consoles["tag"]
            if self.project_root:
                with console.task("Listing tags...", spinner="dots"):
                    tag_command(self.project_root, console=console, action=TagAction.LIST, limit=20)
        finally:
            self._set_button_loading("list-tags-btn", False)

    @work(thread=True)
    def run_delete_tag(self) -> None:
        """Run delete tag - placeholder."""
        console = self._consoles["tag"]
        console.print_warning("Delete tag requires tag name. Use CLI for now.")

    @work(thread=True)
    def run_show_version(self) -> None:
        """Run show version."""
        self._set_button_loading("show-version-btn", True)
        try:
            console = self._consoles["version"]
            if self.project_root:
                with console.task("Getting version information...", spinner="dots"):
                    version_command(self.project_root, console=console)
        finally:
            self._set_button_loading("show-version-btn", False)

    @work(thread=True)
    def run_show_config(self) -> None:
        """Run show config."""
        self._set_button_loading("show-config-btn", True)
        try:
            console = self._consoles["config"]
            from ..presentation import render_config

            with console.task("Loading configuration...", spinner="dots"):
                config = self.config_manager.load()
                render_config(console, config, DEFAULT_CONFIG_FILE)
        finally:
            self._set_button_loading("show-config-btn", False)
