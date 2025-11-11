"""Configuration data models."""

from dataclasses import dataclass


@dataclass
class ConfigData:
    """Configuration data structure."""

    env_root: str | None = None
    target_path: str | None = None
