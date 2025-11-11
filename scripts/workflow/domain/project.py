"""Project root and target path detection - pure business logic."""

from pathlib import Path

from ..types import ConfigData


def find_project_root(path: Path | None = None) -> Path | None:
    """Find project root by looking for pyproject.toml.

    Pure function - no console output, no errors raised.
    Returns None if not found.

    Args:
        path: Optional starting path (defaults to current directory)

    Returns:
        Path to project root if found, None otherwise

    """
    if path:
        if path.exists() and (path / "pyproject.toml").exists():
            return path
        return None

    # Search from current directory up
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent

    return None


def validate_project_root(path: Path) -> bool:
    """Validate if path is a valid project root.

    Args:
        path: Path to validate

    Returns:
        True if path exists and contains pyproject.toml

    """
    return path.exists() and (path / "pyproject.toml").exists()


def find_target_path(config: ConfigData, default: Path | None = None) -> Path | None:
    """Resolve target path from config or default.

    Args:
        config: Configuration data
        default: Default target path if not in config

    Returns:
        Target path or None

    """
    if config.target_path:
        target = Path(config.target_path)
        if target.exists():
            return target

    return default

