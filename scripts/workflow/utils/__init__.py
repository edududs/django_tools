"""Workflow utilities - backward compatibility layer."""

# Re-export from new locations for backward compatibility
from ..domain.version import calculate_next_version
from ..infrastructure import (
    count_commits_to_push,
    get_current_branch,
    get_current_version,
    get_unpushed_tags,
    has_uncommitted_changes,
)

__all__ = [
    "calculate_next_version",
    "count_commits_to_push",
    "get_current_branch",
    "get_current_version",
    "get_unpushed_tags",
    "has_uncommitted_changes",
]
