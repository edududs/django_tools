"""Configuration management for workflow."""

import json
from pathlib import Path

from rich.console import Console

console = Console()


class WorkflowConfig:
    """Manage workflow configuration."""

    def __init__(self):
        self.config_file = Path.home() / ".workflow_config.json"

    def get_config(self) -> dict:
        """Get current configuration.

        Returns:
            Configuration dictionary

        """
        if not self.config_file.exists():
            return {}

        try:
            return json.loads(self.config_file.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def get_env_root(self) -> Path | None:
        """Get configured environment root.

        Returns:
            Path to environment root or None if not configured

        """
        config = self.get_config()
        env_root = config.get("env_root")
        if env_root:
            return Path(env_root)
        return None

    def set_env_root(self, env_root: Path) -> None:
        """Set environment root.

        Args:
            env_root: Path to environment root directory

        """
        config = self.get_config()
        config["env_root"] = str(env_root.resolve())
        self.config_file.write_text(json.dumps(config, indent=2))

    def clear_env_root(self) -> None:
        """Clear environment root configuration."""
        config = self.get_config()
        if "env_root" in config:
            del config["env_root"]
        if config:
            self.config_file.write_text(json.dumps(config, indent=2))
        else:
            self.config_file.unlink(missing_ok=True)

    def get_target_path(self) -> Path | None:
        """Get configured target path for validation.

        Returns:
            Path to target directory or None if not configured

        """
        config = self.get_config()
        target_path = config.get("target_path")
        if target_path:
            return Path(target_path)
        return None

    def set_target_path(self, target_path: Path) -> None:
        """Set target path for validation.

        Args:
            target_path: Path to target directory

        """
        config = self.get_config()
        config["target_path"] = str(target_path.resolve())
        self.config_file.write_text(json.dumps(config, indent=2))

    def clear_target_path(self) -> None:
        """Clear target path configuration."""
        config = self.get_config()
        if "target_path" in config:
            del config["target_path"]
        if config:
            self.config_file.write_text(json.dumps(config, indent=2))
        else:
            self.config_file.unlink(missing_ok=True)

    def show_config(self) -> None:
        """Display current configuration."""
        config = self.get_config()

        if not config:
            console.print("[yellow]No configuration found.[/yellow]")
            console.print("\n[dim]Use 'workflow config set-env' to configure an environment.[/dim]")
            return

        console.print("[bold cyan]Current Configuration:[/bold cyan]\n")

        if "env_root" in config:
            console.print(f"[green]Environment Root:[/green] {config['env_root']}")
        else:
            console.print("[dim]Environment Root: Not configured[/dim]")

        if "target_path" in config:
            console.print(f"[green]Target Path:[/green] {config['target_path']}")
        else:
            console.print("[dim]Target Path: Not configured[/dim]")

        console.print(f"\n[dim]Config file: {self.config_file}[/dim]")


# Global config instance
workflow_config = WorkflowConfig()
