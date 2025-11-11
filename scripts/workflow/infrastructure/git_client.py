"""Git client - pure git operations via subprocess."""

import re
import subprocess
from pathlib import Path

from .file_system import read_pyproject


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


def count_commits_to_push(branch: str) -> int:
    """Count commits that need to be pushed.

    Args:
        branch: Branch name

    Returns:
        Number of commits to push

    """
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


def get_current_version(project_root: Path) -> str:
    """Extract current version from pyproject.toml.

    Args:
        project_root: Project root directory

    Returns:
        Current version string (e.g., "0.3.3")

    Raises:
        FileNotFoundError: If pyproject.toml not found
        ValueError: If version not found in pyproject.toml

    """
    content = read_pyproject(project_root)
    match = re.search(r'version = "([^"]+)"', content)

    if not match:
        msg = "Could not find version in pyproject.toml"
        raise ValueError(msg)

    return match.group(1)
