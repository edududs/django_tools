"""Version management - pure version logic."""

import re


def get_version_from_pyproject(content: str) -> str:
    """Extract version from pyproject.toml content.

    Args:
        content: pyproject.toml file content

    Returns:
        Version string (e.g., "0.3.3")

    Raises:
        ValueError: If version not found

    """
    match = re.search(r'version = "([^"]+)"', content)

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
        return tuple(map(int, version_parts))
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


def calculate_next_version(current_version: str, bump_type: str) -> str:
    """Calculate next version based on bump type.

    Args:
        current_version: Current version (e.g., "0.3.3")
        bump_type: Type of bump ("patch", "minor", "major")

    Returns:
        Next version string

    Raises:
        ValueError: If version format or bump type is invalid

    """
    major, minor, patch = parse_version(current_version)

    if bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    if bump_type == "major":
        return f"{major + 1}.0.0"

    msg = f"Invalid bump type: {bump_type}. Must be 'patch', 'minor', or 'major'"
    raise ValueError(msg)

