"""File system operations - pure file I/O."""

from pathlib import Path


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
