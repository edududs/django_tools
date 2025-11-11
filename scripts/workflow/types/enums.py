"""Enums for workflow types."""

from enum import StrEnum


class BumpType(StrEnum):
    """Version bump types."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class TagAction(StrEnum):
    """Tag management actions."""

    CREATE = "create"
    LIST = "list"
    DELETE = "delete"
