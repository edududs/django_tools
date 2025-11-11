"""Git operations orchestration - business logic for git decisions."""


def should_push_commits(commits_count: int, force: bool) -> bool:
    """Determine if commits should be pushed.

    Args:
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
