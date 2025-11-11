"""Configuration manager - pure file I/O for configuration."""

import json
from dataclasses import asdict
from pathlib import Path

from ..types import ConfigData


class ConfigManager:
    """Manage workflow configuration - pure I/O operations."""

    def __init__(self, config_file: Path):
        """Initialize config manager.

        Args:
            config_file: Path to configuration file

        """
        self.config_file = config_file

    def load(self) -> ConfigData:
        """Load configuration from file.

        Returns:
            ConfigData with loaded configuration

        """
        if not self.config_file.exists():
            return ConfigData()

        try:
            data = json.loads(self.config_file.read_text())
            return ConfigData(
                env_root=data.get("env_root"),
                target_path=data.get("target_path"),
            )
        except (json.JSONDecodeError, OSError):
            return ConfigData()

    def save(self, config: ConfigData) -> None:
        """Save configuration to file.

        Args:
            config: ConfigData to save

        """
        data = asdict(config)
        self.config_file.write_text(json.dumps(data, indent=2))

    def get_env_root(self) -> Path | None:
        """Get configured environment root.

        Returns:
            Path to environment root or None if not configured

        """
        config = self.load()
        if config.env_root:
            return Path(config.env_root)
        return None

    def set_env_root(self, env_root: Path) -> None:
        """Set environment root.

        Args:
            env_root: Path to environment root directory

        """
        config = self.load()
        config.env_root = str(env_root.resolve())
        self.save(config)

    def clear_env_root(self) -> None:
        """Clear environment root configuration."""
        config = self.load()
        config.env_root = None
        if config.env_root is None and config.target_path is None:
            self.config_file.unlink(missing_ok=True)
        else:
            self.save(config)

    def get_target_path(self) -> Path | None:
        """Get configured target path for validation.

        Returns:
            Path to target directory or None if not configured

        """
        config = self.load()
        if config.target_path:
            return Path(config.target_path)
        return None

    def set_target_path(self, target_path: Path) -> None:
        """Set target path for validation.

        Args:
            target_path: Path to target directory

        """
        config = self.load()
        config.target_path = str(target_path.resolve())
        self.save(config)

    def clear_target_path(self) -> None:
        """Clear target path configuration."""
        config = self.load()
        config.target_path = None
        if config.env_root is None and config.target_path is None:
            self.config_file.unlink(missing_ok=True)
        else:
            self.save(config)

    def clear(self) -> None:
        """Clear all configuration."""
        self.config_file.unlink(missing_ok=True)
