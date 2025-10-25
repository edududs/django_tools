.PHONY: help clean ruff-fix ruff-check ruff-format workflow-check workflow-run workflow-version dry-push push commit-push

help:
	@echo "Available commands:"
	@echo ""
	@echo "Ruff Commands:"
	@echo "  ruff-fix      - Format and fix code with Ruff (auto-fix lint and formatting issues)"
	@echo "  ruff-check    - Check code formatting and linting (does not modify files)"
	@echo "  ruff-format   - Check code formatting only (no lint checks)"
	@echo ""
	@echo "Workflow Commands:"
	@echo "  workflow-check    - Quick check (linting + formatting)"
	@echo "  workflow-run      - Full workflow simulation (tests + release dry-run)"
	@echo "  workflow-version  - Show current version and next possible versions"
	@echo "  dry-push          - Run version, check, workflow, and clean in sequence"
	@echo ""
	@echo "Git Commands:"
	@echo "  push              - Run full validation and push committed changes (allows uncommitted files)"
	@echo "  commit-push       - Add all changes, commit with message, and push"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean             - Remove Python cache, egg-info, and lock/generated files"
	@echo ""
	@echo "Usage: make <command>"

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.egg-info" -delete
	find . -name "*.egg" -delete
	find . -name "*.eggs" -delete
	find . -name "*.ruff_cache" -delete
	find . -name "*.mypy_cache" -delete
	find . -name "*.pytest_cache" -delete
	find . -name "*.typed" -delete
	find . -name "*.lock" -delete


ruff-fix:
	uv run ruff format --check src/
	uv run ruff check src/ --fix

ruff-check:
	uv run ruff format src/ --check
	uv run ruff check src/

ruff-format:
	uv run ruff format --check src/

# Workflow Dry Run Commands
workflow-check:
	uv run python scripts/workflow_dryrun.py check

workflow-run:
	uv run python scripts/workflow_dryrun.py run

workflow-version:
	uv run python scripts/workflow_dryrun.py version

dry-push: workflow-version workflow-check workflow-run clean

push: workflow-check workflow-run
	@echo ""
	@echo "🔍 Checking if there are commits to push..."
	@if ! git rev-list --count HEAD ^origin/$$(git branch --show-current) > /dev/null 2>&1 || [ $$(git rev-list --count HEAD ^origin/$$(git branch --show-current)) -eq 0 ]; then \
		echo "❌ No commits to push. Your branch is up to date with remote."; \
		exit 1; \
	fi
	@echo "✅ Found commits to push."
	@echo ""
	@echo "🚀 All validations passed! Pushing to remote..."
	@echo ""
	git push
	@echo ""
	@echo "✅ Push completed successfully!"

commit-push:
	@echo "🔍 Checking for changes to commit..."
	@if [ -z "$$(git status --porcelain)" ]; then \
		echo "❌ No changes to commit."; \
		exit 1; \
	fi
	@echo "✅ Found changes to commit."
	@echo ""
	@echo "📝 Please enter your commit message:"
	@read -p "Commit message: " msg; \
	if [ -z "$$msg" ]; then \
		echo "❌ Commit message cannot be empty."; \
		exit 1; \
	fi; \
	echo ""; \
	echo "🔄 Adding all changes..."; \
	git add .; \
	echo "📝 Committing with message: $$msg"; \
	git commit -m "$$msg"; \
	echo ""; \
	echo "🚀 Running validations before push..."; \
	$(MAKE) push
