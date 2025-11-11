# pyright: reportAttributeAccessIssue=false
"""Version management - pure version logic."""

from ..types import BumpType
from ..utils.constants import VERSION_PATTERN


def get_version_from_pyproject(content: str) -> str:
    """Extract version from pyproject.toml content.

    Args:
        content: pyproject.toml file content

    Returns:
        Version string (e.g., "0.3.3")

    Raises:
        ValueError: If version not found

    """
    match = VERSION_PATTERN.search(content)

    if not match:
        msg = "Could not find version in pyproject.toml"
        raise ValueError(msg)

    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string into parts.

    Args:
        version: Version string (e.g., "0.3.3")

    Returns:
        Tuple of (major, minor, patch)

    Raises:
        ValueError: If version format is invalid

    """
    version_parts = version.split(".")
    if len(version_parts) != 3:
        msg = f"Invalid version format: {version}"
        raise ValueError(msg)

    try:
        return tuple(map(int, version_parts))  # pyright: ignore[reportReturnType]
    except ValueError as e:
        msg = f"Invalid version format: {version}"
        raise ValueError(msg) from e


def validate_version_format(version: str) -> bool:
    """Validate version format.

    Args:
        version: Version string to validate

    Returns:
        True if format is valid (X.Y.Z), False otherwise

    """
    try:
        parse_version(version)
        return True
    except ValueError:
        return False


def calculate_next_version(current_version: str, bump_type: str | BumpType) -> str:
    """Calculate next version based on bump type.

    Args:
        current_version: Current version (e.g., "0.3.3")
        bump_type: Type of bump ("patch", "minor", "major" or BumpType enum)

    Returns:
        Next version string

    Raises:
        ValueError: If version format or bump type is invalid

    """
    major, minor, patch = parse_version(current_version)

    # Normalize to string for comparison
    bump_str = bump_type.value if isinstance(bump_type, BumpType) else bump_type

    match bump_str:
        case BumpType.PATCH.value:
            return f"{major}.{minor}.{patch + 1}"
        case BumpType.MINOR.value:
            return f"{major}.{minor + 1}.0"
        case BumpType.MAJOR.value:
            return f"{major + 1}.0.0"
        case _:
            msg = f"Invalid bump type: {bump_type}. Must be 'patch', 'minor', or 'major'"
            raise ValueError(msg)
