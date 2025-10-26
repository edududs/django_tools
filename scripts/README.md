# Workflow Automation System

Modular automation system for code quality and release management.

## Overview

The workflow system is your **command center** to ensure code quality before pushing. It integrates validations (Ruff, Pyright, tests) with Git operations (push, tags, releases) in a modular and extensible way.

## Installation

All dependencies are included in `pyproject.toml`:

```bash
uv sync --dev
```

## Architecture

```
scripts/workflow/
├── cli.py              # Main CLI interface
├── config.py           # Configuration management
├── core/               # Core components
│   ├── models.py       # CommandResult, JobResult
│   └── runner.py       # WorkflowRunner
├── commands/           # Modular commands
│   ├── check.py        # Validations (ruff, pyright, tests)
│   ├── push.py         # Push operations
│   ├── tag.py          # Tag management
│   └── version.py      # Version information
└── utils/              # Utilities
    └── git.py          # Git functions
```

## Configuration System

The workflow supports **persistent configuration** to use one environment's settings to validate code anywhere in your system.

### Configuration File

Configuration is stored in `~/.workflow_config.json` and includes:

- **Environment Root**: Where `pyproject.toml` and dependencies are located
- **Target Path**: Where to validate code (optional, defaults to `src/`)

### Configuration Commands

```bash
# Show current configuration
make config show

# Set environment root (where pyproject.toml is)
make config set-env -- --path /path/to/environment

# Set target path (where to validate code)
make config set-target -- --path /path/to/validate

# Clear all configuration
make config clear
```

### Configuration Workflow

**Scenario 1: Validate multiple projects with same rules**

```bash
# Configure environment once
make config set-env -- --path /home/user/main-environment

# Validate different projects using same environment
make check -- --path /project1
make check -- --path /project2
make check -- --path /project3
```

**Scenario 2: Fixed environment + fixed target**

```bash
# Configure once
make config set-env -- --path /my/environment
make config set-target -- --path /my/code

# Use always
make check
make full
```

**Scenario 3: Normal development**

```bash
# No configuration, uses current directory
make check
make full
make push
```

## Usage via Makefile (Recommended)

All Makefile commands support **dynamic arguments** using the pattern:

```bash
make command [args...]
```

Use `--` to separate Make options from command arguments:

```bash
make command -- --flag value
```

### Validation Commands

```bash
# Quick check (Ruff only)
make check

# Quick check with auto-fix
make check-fix

# Check with custom arguments
make check -- --fix --path /custom/path

# Full check (Ruff + Pyright + Tests)
make full

# Full check with auto-fix
make full-fix

# Full check with custom arguments
make full -- --skip-pyright --fix
```

### Push Commands

```bash
# Push with automatic validation
make push

# Force push (no validation - use with caution!)
make push-force

# Push only tags
make push-tags

# Push with custom arguments
make push -- --tags-only --no-validate
```

### Release Commands

```bash
# Create release tag (validates first)
make release

# Create tag and push immediately
make release-push

# Release with custom arguments
make release -- --push --no-validate
```

### Tag Commands

```bash
# List recent tags
make tag-list

# Create tag manually
make tag-create

# Create tag and push
make tag-create-push

# Tag with custom arguments
make tag list -- --limit 20
make tag create -- --push
make tag delete -- --name v1.0.0 --remote
```

### Utility Commands

```bash
# Show current and next versions
make version

# Version with custom path
make version -- --path /other/project

# Complete deployment (validation + push all)
make deploy

# Deploy with custom arguments
make deploy -- --skip-validation
```

## Direct CLI Usage

### Validations

```bash
# Ruff only
uv run python -m scripts.workflow.cli check

# Ruff with auto-fix
uv run python -m scripts.workflow.cli check --fix

# Add Pyright
uv run python -m scripts.workflow.cli check --pyright

# Add tests
uv run python -m scripts.workflow.cli check --tests

# Everything together
uv run python -m scripts.workflow.cli full

# Everything with auto-fix
uv run python -m scripts.workflow.cli full --fix

# Skip Pyright
uv run python -m scripts.workflow.cli full --skip-pyright

# Skip tests
uv run python -m scripts.workflow.cli full --skip-tests

# Custom path
uv run python -m scripts.workflow.cli check --path /custom/path
```

### Push

```bash
# Push with validation
uv run python -m scripts.workflow.cli push

# Push without validation
uv run python -m scripts.workflow.cli push --no-validate

# Force push
uv run python -m scripts.workflow.cli push --force

# Push only tags
uv run python -m scripts.workflow.cli push --tags-only

# Custom path
uv run python -m scripts.workflow.cli push --path /custom/path
```

### Release

```bash
# Create tag (validates first)
uv run python -m scripts.workflow.cli release

# Create tag and push
uv run python -m scripts.workflow.cli release --push

# Create tag without validation
uv run python -m scripts.workflow.cli release --no-validate

# Custom path
uv run python -m scripts.workflow.cli release --path /custom/path
```

### Tags

```bash
# List tags
uv run python -m scripts.workflow.cli tag list

# List more tags
uv run python -m scripts.workflow.cli tag list --limit 20

# Create tag
uv run python -m scripts.workflow.cli tag create

# Create tag and push
uv run python -m scripts.workflow.cli tag create --push

# Delete local tag
uv run python -m scripts.workflow.cli tag delete --name v1.0.0

# Delete local and remote tag
uv run python -m scripts.workflow.cli tag delete --name v1.0.0 --remote

# Custom path
uv run python -m scripts.workflow.cli tag list --path /custom/path
```

### Version

```bash
# Show version information
uv run python -m scripts.workflow.cli version

# Custom path
uv run python -m scripts.workflow.cli version --path /custom/path
```

### Deploy

```bash
# Complete deployment (validation + push)
uv run python -m scripts.workflow.cli deploy

# Deploy without validation (not recommended)
uv run python -m scripts.workflow.cli deploy --skip-validation

# Custom path
uv run python -m scripts.workflow.cli deploy --path /custom/path
```

### Configuration

```bash
# Show configuration
uv run python -m scripts.workflow.cli config show

# Set environment root
uv run python -m scripts.workflow.cli config set-env --path /path/to/env

# Set target path
uv run python -m scripts.workflow.cli config set-target --path /path/to/target

# Clear configuration
uv run python -m scripts.workflow.cli config clear
```

## Recommended Workflows

### 1. Normal Development

```bash
# During development
make check-fix          # Validate and fix Ruff

# Before committing
make full               # Complete validation

# After committing
make push               # Push with validation
```

### 2. Release with Tag

```bash
# 1. Update version in pyproject.toml manually
vim pyproject.toml      # Change version = "X.Y.Z"

# 2. Commit version change
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"

# 3. Create tag and push
make release-push       # Validates, creates tag, and pushes
```

### 3. Quick Deploy

```bash
# After committing your changes
make deploy             # Validates everything and pushes
```

### 4. Urgent Fix (Hotfix)

```bash
# Minimal validation + push
make check
make push-force         # Skips full validation
```

### 5. Multi-Project Validation

```bash
# Configure environment once
make config set-env -- --path /home/user/main-project

# Validate different directories
make check -- --path /project-a/src
make check -- --path /project-b/lib
make check -- --path /project-c/app
```

## What Each Command Validates

### `check` (Ruff)

- ✅ Ruff installation
- ✅ Linting (with or without auto-fix)
- ✅ Formatting (with or without auto-fix)

### `full` (Complete)

- ✅ Ruff (linting + formatting)
- ✅ Pyright (type checking)
- ✅ Pytest (tests with coverage)

### `push` (Push with Validation)

- ✅ Ruff checks
- ✅ Checks if there are commits to push
- ✅ Push commits
- ✅ Push tags (if any)

### `release` (Release with Tag)

- ✅ Complete validation (Ruff + Pyright + Tests)
- ✅ Reads version from pyproject.toml
- ✅ Creates annotated tag (v{version})
- ✅ Optionally pushes the tag

### `deploy` (Complete Deploy)

- ✅ Complete validation
- ✅ Push commits
- ✅ Push tags

## Differences from Old System

### Before (`workflow_dryrun.py`)

- Monolithic (single file)
- Simulated CI/CD locally
- Automatic release in CI/CD

### Now (`workflow` Package)

- **Modular**: Clear separation of responsibilities
- **Extensible**: Easy to add new commands
- **Local control**: Manual releases via CLI
- **Simplified CI/CD**: Tests only, no releases
- **Configuration system**: Validate code anywhere with any environment

## CI/CD Integration

CI/CD is now **for validation only**:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    - Run Ruff linting
    - Run tests
```

**Releases are done locally** via `make release-push`.

## Error Output

The system provides **detailed error information**:

- Specific commands that failed
- Error output in red
- Structured summary of failed checks
- Helpful tips for fixing (e.g., use `--fix`)

Example output on failure:

```
❌ Ruff checks failed with errors:

Failed command: Run Ruff format check

Would reformat: src/file.py
1 file would be reformatted

✗ Some checks failed

Failed checks:
  • RUFF: 1 command(s) failed

💡 Tip: Run with --fix to auto-fix some issues.
```

## Troubleshooting

### Script can't find pyproject.toml

```bash
cd /path/to/django_tools
# or
make config set-env -- --path /path/to/project
```

### Tests failing

```bash
uv run pytest src/ -v
```

### Ruff finds errors

```bash
make check-fix
```

### Pyright finds errors

```bash
pyright
# or
make pyright
```

### Push fails due to no commits

```bash
# Check if there are commits to push
git status
git log origin/main..HEAD
```

### Tag already exists

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0

# Or use the command
make tag-list
uv run python -m scripts.workflow.cli tag delete --name v1.0.0 --remote
```

### Configuration issues

```bash
# Show current configuration
make config show

# Clear and reconfigure
make config clear
make config set-env -- --path /correct/path
```

## Legacy Commands (Direct Ruff)

Still available for compatibility:

```bash
make ruff-fix           # Ruff format + check --fix
make ruff-check         # Ruff format --check + check
make ruff-format        # Ruff format --check
```

**Recommendation**: Use the new commands `make check` and `make full`.

## Dependencies

- `typer`: CLI framework
- `rich`: Rich terminal visualization
- `pytest`: Test framework
- `ruff`: Linter and formatter
- `pyright`: Type checker (optional)

All automatically installed with `uv sync --dev`.

## Contributing

To add new commands:

1. Create module in `scripts/workflow/commands/`
2. Implement function `{command}_command(project_root, ...)`
3. Export in `scripts/workflow/commands/__init__.py`
4. Add command in `cli.py`
5. Add shortcut in `Makefile`

Example:

```python
# scripts/workflow/commands/mycommand.py
def mycommand_command(project_root: Path, target_path: Path | None = None) -> bool:
    runner = WorkflowRunner(project_root)
    # ... implementation
    return True
```

```python
# scripts/workflow/cli.py
@app.command()
def mycommand(
    path: str = typer.Option(None, "--path", help="Project root directory"),
):
    """My custom command."""
    project_root = get_project_root(path)
    target_path = get_target_path()
    success = mycommand_command(project_root, target_path)
    if not success:
        raise typer.Exit(1)
```

```makefile
# Makefile
mycommand:
 uv run python -m scripts.workflow.cli mycommand $(filter-out $@,$(MAKECMDGOALS))
```

## Advanced Features

### Dynamic Arguments in Makefile

The Makefile uses `$(filter-out $@,$(MAKECMDGOALS))` to pass arguments dynamically:

```bash
# All these work:
make check --fix
make check --path /custom/path --fix
make full --skip-pyright --skip-tests
make tag list --limit 50
make config set-env --path /my/env
```

**Note**: Use `--` to separate Make options from command arguments when needed:

```bash
make config set-env -- --path /path/with/spaces
```

### Configuration Persistence

Configuration is stored in `~/.workflow_config.json`:

```json
{
  "env_root": "/home/user/main-project",
  "target_path": "/home/user/code-to-validate"
}
```

This allows you to:

- Set up once, use everywhere
- Validate code in any directory with consistent rules
- Switch between projects easily
- Share configurations across team members

### Priority Order

When determining which path to use:

1. **`--path` argument** (highest priority, temporary override)
2. **Configured env_root** (from `config set-env`)
3. **Current directory** (default fallback)

When determining target path:

1. **Configured target_path** (from `config set-target`)
2. **`src/` directory** (default)
