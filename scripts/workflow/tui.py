"""Textual TUI entry point."""

from pathlib import Path

from .presentation.textual_app import WorkflowApp


def main() -> None:
    """Run Textual TUI."""
    # Set CSS path relative to this file
    css_path = Path(__file__).parent / "presentation" / "workflow.tcss"
    app = WorkflowApp()
    app.CSS_PATH = str(css_path)
    app.run()


if __name__ == "__main__":
    main()

