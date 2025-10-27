# Workflow Examples

This directory contains practical examples of how to use the workflow system's dependency injection containers.

## Examples

### `container_usage.py`

Demonstrates how to use the workflow containers individually and in combination:

- **Individual Containers**: How to use `UtilsContainer`, `CoreContainer`, and `CommandsContainer` separately
- **WorkflowContainer**: The main orchestrator that composes all sub-containers
- **Dependency Injection Flow**: How dependencies are resolved through the container hierarchy
- **Testing with Overrides**: How to use `provider.override()` for mocking in tests
- **CLI Integration**: How the CLI integrates with the container system

## Running the Examples

```bash
# Run the container usage example
uv run python -m examples.workflow.container_usage
```

## Key Concepts Demonstrated

### Container Hierarchy

```text
WorkflowContainer (Main orchestrator)
├── ConfigManager (Singleton)           # Configuration persistence
├── CoreContainer
│   ├── Console (Singleton)             # Rich terminal output
│   └── WorkflowRunner (Factory)        # Command execution
├── UtilsContainer
│   └── Git utilities (Callable)       # Pure functions
└── CommandsContainer
    └── Workflow commands (Callable)    # Commands with injected dependencies
```

### Entry Point

The `WorkflowContainer` is the main entry point that orchestrates everything:

```python
from scripts.workflow.containers import WorkflowContainer

# Create container instance
workflow_container = WorkflowContainer()

# Get dependencies
config_manager = workflow_container.config()
console = workflow_container.core.console()
commands = workflow_container.commands()

# Execute commands
check_command = commands.check_command()
success = check_command(project_root, target_path)
```

### Testing with Overrides

```python
from unittest.mock import Mock

# Mock dependencies
mock_config = Mock(spec=ConfigManager)
mock_console = Mock()

# Override providers
with (
    workflow_container.config.override(mock_config),
    workflow_container.core.console.override(mock_console),
):
    # Test with mocked dependencies
    commands = workflow_container.commands()
    check_command = commands.check_command()
    # ... test logic
```

## Benefits

- **Automatic Dependency Resolution**: No manual wiring needed
- **Easy Testing**: Simple mocking with `provider.override()`
- **Clean Architecture**: Clear separation of concerns
- **Type Safety**: Full type hints throughout
- **Flexible**: Can use containers individually or together
