"""Configuration data models."""

from dataclasses import dataclass


@dataclass
class ConfigData:
    """Configuration data structure."""

    env_root: str | None = None
    target_path: str | None = None


class ConfigKeys:
    """Configuration keys constants."""

    ENV_ROOT = "env_root"
    TARGET_PATH = "target_path"
