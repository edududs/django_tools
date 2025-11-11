"""Git operations orchestration - business logic for git decisions."""


def should_push_commits(branch: str, commits_count: int, force: bool) -> bool:
    """Determine if commits should be pushed.

    Args:
        branch: Branch name
        commits_count: Number of commits to push
        force: Whether force push is requested

    Returns:
        True if commits should be pushed

    """
    return commits_count > 0 or force


def should_push_tags(tags_count: int) -> bool:
    """Determine if tags should be pushed.

    Args:
        tags_count: Number of unpushed tags

    Returns:
        True if tags should be pushed

    """
    return tags_count > 0


def can_force_push(force: bool, has_uncommitted: bool) -> bool:
    """Determine if force push is safe/allowed.

    Args:
        force: Whether force push is requested
        has_uncommitted: Whether there are uncommitted changes

    Returns:
        True if force push can proceed

    """
    # Business rule: force push is allowed if explicitly requested
    # Additional safety checks can be added here
    return force

