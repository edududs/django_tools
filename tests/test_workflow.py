# pyright: reportMissingImports=false, reportUndefinedVariable=false, reportMissingParameterType=false
"""Testes essenciais para verificar se a refatoração do workflow não quebrou nada."""

import pytest  # noqa: F401

from scripts.workflow.domain.project import find_project_root, validate_project_root
from scripts.workflow.domain.version import (
    calculate_next_version,
    parse_version,
    validate_version_format,
)
from scripts.workflow.infrastructure import ConfigManager, execute_command, get_current_version
from scripts.workflow.types import ConfigData, ExecutionResult


class TestDomain:
    """Testes da camada domain."""

    def test_find_project_root(self):
        """Testa detecção de project root."""
        root = find_project_root()
        assert root is not None
        assert (root / "pyproject.toml").exists()

    def test_validate_project_root(self, tmp_path):
        """Testa validação de project root."""
        # Invalid - no pyproject.toml
        assert not validate_project_root(tmp_path)

        # Valid - with pyproject.toml
        (tmp_path / "pyproject.toml").write_text('version = "0.1.0"')
        assert validate_project_root(tmp_path)

    def test_calculate_next_version(self):
        """Testa cálculo de próxima versão."""
        assert calculate_next_version("0.1.0", "patch") == "0.1.1"
        assert calculate_next_version("0.1.0", "minor") == "0.2.0"
        assert calculate_next_version("0.1.0", "major") == "1.0.0"

    def test_parse_version(self):
        """Testa parsing de versão."""
        assert parse_version("1.2.3") == (1, 2, 3)
        assert parse_version("0.4.4") == (0, 4, 4)

    def test_validate_version_format(self):
        """Testa validação de formato de versão."""
        assert validate_version_format("1.2.3")
        assert validate_version_format("0.4.4")
        assert not validate_version_format("invalid")
        assert not validate_version_format("1.2")


class TestInfrastructure:
    """Testes da camada infrastructure."""

    def test_execute_command(self, tmp_path):
        """Testa execução de comando."""
        result = execute_command("echo 'test'", cwd=tmp_path)
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert "test" in result.stdout

    def test_config_manager(self, tmp_path):
        """Testa gerenciamento de configuração."""
        config_file = tmp_path / "test_config.json"
        manager = ConfigManager(config_file)

        # Load empty config
        config = manager.load()
        assert isinstance(config, ConfigData)
        assert config.env_root is None

        # Set and get env_root
        test_path = tmp_path / "test_env"
        test_path.mkdir()
        manager.set_env_root(test_path)
        assert manager.get_env_root() == test_path

        # Clear
        manager.clear()
        assert manager.get_env_root() is None

    def test_get_current_version(self):
        """Testa obtenção de versão atual."""
        # Assume we're in the project root
        project_root = find_project_root()
        if project_root and (project_root / "pyproject.toml").exists():
            version = get_current_version(project_root)
            assert version
            assert validate_version_format(version)


class TestIntegration:
    """Testes de integração básicos."""

    def test_workflow_imports(self):
        """Testa se todos os imports principais funcionam."""
        from scripts.workflow import app
        from scripts.workflow.commands import (
            check_command,
            push_command,
            tag_command,
            version_command,
        )

        assert app is not None
        assert check_command is not None
        assert push_command is not None
        assert tag_command is not None
        assert version_command is not None

    def test_version_command_integration(self):
        """Testa integração do comando version."""
        project_root = find_project_root()
        if project_root:
            from scripts.workflow.commands import version_command

            # Should not raise
            result = version_command(project_root)
            assert isinstance(result, bool)
