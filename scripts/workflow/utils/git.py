"""Git utility functions."""

import re
import subprocess
from pathlib import Path


def get_current_version(project_root: Path) -> str:
    """Extract current version from pyproject.toml.

    Args:
        project_root: Project root directory

    Returns:
        Current version string (e.g., "0.3.3")

    Raises:
        ValueError: If version not found in pyproject.toml

    """
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        msg = "pyproject.toml not found"
        raise FileNotFoundError(msg)

    content = pyproject.read_text()
    match = re.search(r'version = "([^"]+)"', content)

    if not match:
        msg = "Could not find version in pyproject.toml"
        raise ValueError(msg)

    return match.group(1)


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
    version_parts = current_version.split(".")
    if len(version_parts) != 3:
        msg = f"Invalid version format: {current_version}"
        raise ValueError(msg)

    major, minor, patch = map(int, version_parts)

    if bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    if bump_type == "major":
        return f"{major + 1}.0.0"
    msg = f"Invalid bump type: {bump_type}. Must be 'patch', 'minor', or 'major'"
    raise ValueError(msg)


def get_current_branch() -> str:
    """Get current git branch name.

    Returns:
        Current branch name

    Raises:
        RuntimeError: If git command fails

    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        msg = f"Failed to get current branch: {e}"
        raise RuntimeError(msg) from e


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes.

    Returns:
        True if there are uncommitted changes, False otherwise

    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def count_commits_to_push(branch: str | None = None) -> int:
    """Count commits that need to be pushed.

    Args:
        branch: Branch name (defaults to current branch)

    Returns:
        Number of commits to push

    """
    if branch is None:
        branch = get_current_branch()

    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", f"^origin/{branch}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
        return 0
    except (subprocess.CalledProcessError, ValueError):
        return 0


def get_unpushed_tags() -> list[str]:
    """Get list of tags that haven't been pushed to remote.

    Returns:
        List of unpushed tag names

    """
    try:
        # Get all local tags
        local_result = subprocess.run(
            ["git", "tag"],
            capture_output=True,
            text=True,
            check=True,
        )
        local_tags = (
            set(local_result.stdout.strip().split("\n")) if local_result.stdout.strip() else set()
        )

        # Get all remote tags
        remote_result = subprocess.run(
            ["git", "ls-remote", "--tags", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )

        remote_tags = set()
        for line in remote_result.stdout.strip().split("\n"):
            if line:
                # Format: <hash> refs/tags/<tagname>
                parts = line.split("refs/tags/")
                if len(parts) == 2:
                    remote_tags.add(parts[1])

        # Return tags that are local but not remote
        return sorted(local_tags - remote_tags)

    except subprocess.CalledProcessError:
        return []
