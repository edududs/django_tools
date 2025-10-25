.PHONY: ruff-fix ruff-check ruff-format

ruff-fix:
	uv run ruff format --check src/
	uv run ruff check src/ --fix

ruff-check:
	uv run ruff check src/

ruff-format:
	uv run ruff format --check src/