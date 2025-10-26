.PHONY: help clean ruff-fix ruff-check ruff-format check check-fix full full-fix push push-force push-tags release release-push release-force tag tag-list tag-create tag-create-push tag-create-force version deploy config pyright pyright-install

help:
	@echo "Available commands:"
	@echo ""
	@echo "Ruff Commands (legacy):"
	@echo "  ruff-fix      - Format and fix code with Ruff (auto-fix lint and formatting issues)"
	@echo "  ruff-check    - Check code formatting and linting (does not modify files)"
	@echo "  ruff-format   - Check code formatting only (no lint checks)"
	@echo ""
	@echo "Type Checking:"
	@echo "  pyright      - Run Pyright static type checking"
	@echo "  pyright-install - Install Pyright globally via npm"
	@echo ""
	@echo "Workflow Commands (recommended):"
	@echo "  check [ARGS]     - Run Ruff checks (e.g., make check --fix --path /path)"
	@echo "  check-fix        - Run Ruff checks with auto-fix"
	@echo "  full [ARGS]      - Run all checks (e.g., make full --skip-pyright)"
	@echo "  full-fix         - Run all checks with auto-fix"
	@echo "  push [ARGS]      - Push commits/tags (e.g., make push --tags-only)"
	@echo "  push-force       - Force push (skip validation)"
	@echo "  push-tags        - Push only tags"
	@echo "  release [ARGS]   - Create release tag (e.g., make release --push --force)"
	@echo "  release-push     - Create release tag and push it"
	@echo "  release-force    - Create release tag and force push (overwrite existing)"
	@echo "  tag [ARGS]       - Manage tags (e.g., make tag list)"
	@echo "  tag-list         - List recent tags"
	@echo "  tag-create-force - Create tag and force push (overwrite existing)"
	@echo "  version [ARGS]   - Show version info"
	@echo "  deploy [ARGS]    - Complete deployment"
	@echo "  config [ARGS]    - Manage config (e.g., make config show)"
	@echo ""
	@echo "Configuration Examples:"
	@echo "  make config set-env --path /path/to/env"
	@echo "  make config set-target --path /path/to/check"
	@echo "  make config show"
	@echo "  make config clear"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         - Remove Python cache, egg-info, and lock/generated files"
	@echo ""
	@echo "Usage: make <command>"

clean:
	rm -rf \
		__pycache__ \
		*.pyc \
		*.pyo \
		*.egg-info \
		*.egg \
		.eggs \
		build/ \
		dist/ \
		.ruff_cache/ \
		.mypy_cache/ \
		.pytest_cache/ \
		htmlcov/ \
		coverage.xml \
		.tox/ \
		.pyright/ \
		*.typed \
		*.lock \
		.cache/ \
		.pyre/ \
		.pytype/ \
		.nox/ \
		site/ \
		.DS_Store \
		|| true
	find . -name "*.pyc" -type f -delete 2>/dev/null || true
	find . -name "*.pyo" -type f -delete 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pyright" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pyre" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytype" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".nox" -type d -exec rm -rf {} + 2>/dev/null || true



ruff-fix:
	uv run ruff format --check src/
	uv run ruff check src/ --fix

ruff-check:
	uv run ruff format src/ --check
	uv run ruff check src/

ruff-format:
	uv run ruff format --check src/

# Workflow Commands
check:
	uv run python -m scripts.workflow.cli check $(filter-out $@,$(MAKECMDGOALS))

full:
	uv run python -m scripts.workflow.cli full $(filter-out $@,$(MAKECMDGOALS))

push:
	uv run python -m scripts.workflow.cli push $(filter-out $@,$(MAKECMDGOALS))

release:
	uv run python -m scripts.workflow.cli release $(filter-out $@,$(MAKECMDGOALS))

tag:
	uv run python -m scripts.workflow.cli tag $(filter-out $@,$(MAKECMDGOALS))

version:
	uv run python -m scripts.workflow.cli version $(filter-out $@,$(MAKECMDGOALS))

deploy:
	uv run python -m scripts.workflow.cli deploy $(filter-out $@,$(MAKECMDGOALS))

config:
	uv run python -m scripts.workflow.cli config $(filter-out $@,$(MAKECMDGOALS))

# Workflow shortcuts (for convenience)
check-fix:
	uv run python -m scripts.workflow.cli check --fix

full-fix:
	uv run python -m scripts.workflow.cli full --fix

push-force:
	uv run python -m scripts.workflow.cli push --force --no-validate

push-tags:
	uv run python -m scripts.workflow.cli push --tags-only

release-push:
	uv run python -m scripts.workflow.cli release --push

release-force:
	uv run python -m scripts.workflow.cli release --push --force

tag-list:
	uv run python -m scripts.workflow.cli tag list

tag-create:
	uv run python -m scripts.workflow.cli tag create

tag-create-push:
	uv run python -m scripts.workflow.cli tag create --push

tag-create-force:
	uv run python -m scripts.workflow.cli tag create --push --force

# Catch-all target to allow passing arguments
%:
	@:

# Pyright Commands
pyright-install:
	@echo "📦 Installing Pyright globally via npm..."
	npm install -g pyright
	@echo "✅ Pyright installed successfully!"

pyright:
	@echo "🔍 Running Pyright static type checking..."
	@if command -v pyright >/dev/null 2>&1; then \
		pyright; \
	else \
		echo "❌ Pyright not found. Install it first with: make pyright-install"; \
		echo "   Or install via npm: npm install -g pyright"; \
		exit 1; \
	fi
