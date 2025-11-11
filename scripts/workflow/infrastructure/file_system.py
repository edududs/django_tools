"""File system operations - pure file I/O."""

from pathlib import Path


def file_exists(path: Path) -> bool:
    """Check if file exists.

    Args:
        path: File path

    Returns:
        True if file exists, False otherwise

    """
    return path.is_file()


def directory_exists(path: Path) -> bool:
    """Check if directory exists.

    Args:
        path: Directory path

    Returns:
        True if directory exists, False otherwise

    """
    return path.is_dir()


def read_pyproject(project_root: Path) -> str:
    """Read pyproject.toml content.

    Args:
        project_root: Project root directory

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If pyproject.toml not found

    """
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        msg = "pyproject.toml not found"
        raise FileNotFoundError(msg)

    return pyproject.read_text()
