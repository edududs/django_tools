.PHONY: help clean lint lint-fix test test-all type push push-tags release release-full tag tag-list tag-create version deploy config

# ==================================================================================
# Help
# ==================================================================================

help:
	@echo "🚀 Django Tools - Workflow Commands"
	@echo ""
	@echo "📋 Quality Checks:"
	@echo "  make lint          - Run Ruff checks (lint + format)"
	@echo "  make lint-fix       - Run Ruff checks with auto-fix"
	@echo "  make test          - Run tests with coverage"
	@echo "  make test-all      - Run all checks (lint + type + test)"
	@echo "  make type          - Run Pyright type checking"
	@echo ""
	@echo "🚢 Git Operations:"
	@echo "  make push          - Push commits and tags (with validation)"
	@echo "  make push-tags     - Push only tags"
	@echo ""
	@echo "🏷️  Release:"
	@echo "  make release       - Create release tag (current version)"
	@echo "  make release-full  - Full release: fix + validate + push + tag"
	@echo ""
	@echo "📌 Tags:"
	@echo "  make tag           - List recent tags"
	@echo "  make tag-create    - Create tag for current version"
	@echo ""
	@echo "ℹ️  Info:"
	@echo "  make version      - Show current and next versions"
	@echo "  make config       - Show workflow configuration"
	@echo ""
	@echo "🔧 Maintenance:"
	@echo "  make clean        - Remove cache and build files"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make release-full  # Complete release workflow"
	@echo "  make test-all      # Full validation before commit"

# ==================================================================================
# Quality Checks
# ==================================================================================

## Run Ruff checks (lint + format)
lint:
	uv run python -m scripts.workflow.cli check

## Run Ruff checks with auto-fix
lint-fix:
	uv run python -m scripts.workflow.cli check --fix

## Run tests with coverage
test:
	uv run python -m scripts.workflow.cli check --tests --no-ruff --no-pyright

## Run all checks (lint + type + test)
test-all:
	uv run python -m scripts.workflow.cli full

## Run all checks with auto-fix
test-all-fix:
	uv run python -m scripts.workflow.cli full --fix

## Run Pyright type checking
type:
	uv run python -m scripts.workflow.cli check --pyright --no-ruff --no-tests

# ==================================================================================
# Git Operations
# ==================================================================================

## Push commits and tags (with validation)
push:
	uv run python -m scripts.workflow.cli push

## Push only tags
push-tags:
	uv run python -m scripts.workflow.cli push --tags-only

# ==================================================================================
# Release
# ==================================================================================

## Create release tag for current version
release:
	uv run python -m scripts.workflow.cli release --push

## Full release: fix + validate + push commits + create tag + push tag
release-full:
	uv run python -m scripts.workflow.cli release --fix --push-commits --push

# ==================================================================================
# Tags
# ==================================================================================

## List recent tags
tag:
	uv run python -m scripts.workflow.cli tag list

## Create tag for current version
tag-create:
	uv run python -m scripts.workflow.cli tag create

## Create tag and push
tag-create-push:
	uv run python -m scripts.workflow.cli tag create --push

# ==================================================================================
# Info
# ==================================================================================

## Show current and next versions
version:
	uv run python -m scripts.workflow.cli version

## Show workflow configuration
config:
	uv run python -m scripts.workflow.cli config show

## Complete deployment workflow
deploy:
	uv run python -m scripts.workflow.cli deploy

# ==================================================================================
# Maintenance
# ==================================================================================

## Remove cache and build files
clean:
	@echo "🧹 Cleaning cache and build files..."
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
	@echo "✅ Clean complete!"
