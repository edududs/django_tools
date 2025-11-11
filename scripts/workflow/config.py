"""Configuration management for workflow - backward compatibility wrapper."""

from pathlib import Path

from .infrastructure import ConfigManager
from .presentation import RichConsole, render_config

# Default config file path
DEFAULT_CONFIG_FILE = Path.home() / ".workflow_config.json"

console = RichConsole()


class WorkflowConfig:
    """Backward compatibility wrapper for WorkflowConfig.

    This class wraps the new ConfigManager to maintain compatibility
    with existing code that uses workflow_config global instance.
    """

    def __init__(self):
        self.config_file = DEFAULT_CONFIG_FILE
        self._manager = ConfigManager(self.config_file)

    def get_config(self) -> dict[str, str]:
        """Get current configuration as dict (for backward compatibility).

        Returns:
            Configuration dictionary

        """
        config = self._manager.load()
        result = {}
        if config.env_root:
            result["env_root"] = config.env_root
        if config.target_path:
            result["target_path"] = config.target_path
        return result

    def get_env_root(self) -> Path | None:
        """Get configured environment root.

        Returns:
            Path to environment root or None if not configured

        """
        return self._manager.get_env_root()

    def set_env_root(self, env_root: Path) -> None:
        """Set environment root.

        Args:
            env_root: Path to environment root directory

        """
        self._manager.set_env_root(env_root)

    def clear_env_root(self) -> None:
        """Clear environment root configuration."""
        self._manager.clear_env_root()

    def get_target_path(self) -> Path | None:
        """Get configured target path for validation.

        Returns:
            Path to target directory or None if not configured

        """
        return self._manager.get_target_path()

    def set_target_path(self, target_path: Path) -> None:
        """Set target path for validation.

        Args:
            target_path: Path to target directory

        """
        self._manager.set_target_path(target_path)

    def clear_target_path(self) -> None:
        """Clear target path configuration."""
        self._manager.clear_target_path()

    def show_config(self) -> None:
        """Display current configuration."""
        config = self._manager.load()
        render_config(console, config, self.config_file)


# Global config instance for backward compatibility
workflow_config = WorkflowConfig()
