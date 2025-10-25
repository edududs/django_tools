# Workflow Dry Run Script

Script to simulate your CI/CD workflow locally before pushing to GitHub.

## Installation

All dependencies are included in the `pyproject.toml`:

```bash
uv sync --dev
```

## Usage

### Via Makefile (Recommended)

```bash
# List all available commands
make help

# Quick check (linting + formatting)
make workflow-check

# Full workflow (tests + release dry-run)
make workflow-run

# Show version information
make workflow-version

# Git workflow commands
make push              # Run validations and push (if commits exist)
make commit-push       # Add, commit, and push with validations
```

### Via Direct Python

```bash
# Full workflow (dry-run)
uv run python scripts/workflow_dryrun.py run

# Quick check only
uv run python scripts/workflow_dryrun.py check

# Version information
uv run python scripts/workflow_dryrun.py version

# Show help
uv run python scripts/workflow_dryrun.py --help
```

## Output

The script provides:

1. **Real-time execution**: Shows each command as it's run
2. **Summary table**: Job status and success rate
3. **Detailed report**: All executed commands with duration
4. **Test coverage**: Full coverage report

### Example Output

```
╭─────────────────────────────────────╮
│ Workflow Dry Run - CI/CD Simulation │
╰─ Simulating GitHub Actions locally ─╯

╭───────────╮
│ Job: Test │
╰───────────╯

▶ Verify Ruff installation
✓ Verify Ruff installation (0.03s)

▶ Run Ruff linting and auto-fix
✓ Run Ruff linting and auto-fix (0.04s)

...

               Workflow Execution Summary               
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Job  ┃  Status  ┃ Duration ┃ Commands ┃ Success Rate ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ TEST │ ✓ PASSED │    1.09s │   4/4    │              │
└──────┴──────────┴──────────┴──────────┴──────────────┘

╭────────────────────────────────────╮
│ ✓ All jobs completed successfully! │
│ Total duration: 1.09s              │
╰────────────────────────────────────╯
```

## Recommended Workflow

### Option 1: Manual Git Commands

1. **Make your changes and commit them:**

   ```bash
   git add .
   git commit -m "your commit message"
   ```

2. **Before pushing:**

   ```bash
   make push
   ```

### Option 2: Automated Git Workflow

1. **Make your changes and use the automated command:**

   ```bash
   make commit-push
   ```

   This will:
   - Check for changes
   - Ask for commit message
   - Add all changes
   - Commit with your message
   - Run all validations
   - Push if everything passes

### Option 3: Quick Validation Only

```bash
# Before committing (quick check)
make workflow-check

# Before pushing (full validation)
make workflow-run
```

### Advanced Options (Direct Python)

```bash
# Skip the test job
uv run python scripts/workflow_dryrun.py run --skip-tests

# Skip the release job
uv run python scripts/workflow_dryrun.py run --skip-release

# Actually execute release (not recommended, use for testing only)
uv run python scripts/workflow_dryrun.py run --no-dry-run
```

## What the Script Checks

### Job: Test

- ✅ Ruff installation
- ✅ Linting with auto-fix
- ✅ Code formatting
- ✅ Tests with coverage

### Job: Release (Dry Run)

- ✅ Reads the current version
- ✅ Calculates the new version
- ✅ Builds the package
- ⚠️ Does **not** update `pyproject.toml` (dry-run)
- ⚠️ Does **not** create tags (dry-run)

## Troubleshooting

### Script cannot find pyproject.toml

Make sure you are in the project root directory:

```bash
cd /path/to/django_tools
```

### Tests are failing

Run tests manually to view details:

```bash
uv run pytest src/ -v
```

### Ruff finds errors

Run the fix manually:

```bash
uv run ruff check src/ --fix
uv run ruff format src/
```

## Dependencies

- `typer`: CLI framework
- `rich`: Rich terminal visualization
- `pytest`: Test framework
- `ruff`: Linter and formatter

All dependencies are automatically installed with `uv sync --dev`.
