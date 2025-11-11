"""Presentation layer - UI and formatting."""

from .console import ConsoleInterface, RichConsole
from .formatters import (
    create_panel,
    create_table,
    format_command_line,
    format_command_name,
    format_duration,
    format_status,
)
from .renderers import (
    render_command_execution,
    render_config,
    render_job_result,
    render_validation_summary,
)

__all__ = [
    "ConsoleInterface",
    "RichConsole",
    "format_command_name",
    "format_command_line",
    "format_duration",
    "format_status",
    "create_panel",
    "create_table",
    "render_command_execution",
    "render_job_result",
    "render_config",
    "render_validation_summary",
]

