.PHONY: help clean ruff-fix ruff-check ruff-format check check-fix full full-fix push push-force push-tags release release-push release-force tag tag-list tag-create tag-create-push tag-create-force version deploy config pyright pyright-install

# Exibe a ajuda com todos os comandos disponíveis e suas descrições
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

# Remove arquivos de cache, build e artefatos gerados pelo Python e ferramentas
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

# ==================================================================================
# Ruff Commands (legacy - use 'check' workflow command instead)
# ==================================================================================

# Verifica formatação e aplica correções automáticas de lint com Ruff
ruff-fix:
	uv run ruff format --check src/
	uv run ruff check src/ --fix

# Verifica formatação e linting sem modificar arquivos
ruff-check:
	uv run ruff format src/ --check
	uv run ruff check src/

# Verifica apenas formatação de código
ruff-format:
	uv run ruff format --check src/

# ==================================================================================
# Workflow Commands (recommended)
# ==================================================================================

# Executa verificações com Ruff (formatação e linting) com argumentos opcionais
check:
	uv run python -m scripts.workflow.cli check $(filter-out $@,$(MAKECMDGOALS))

# Executa todas as verificações (Ruff + Pyright + testes) com argumentos opcionais
full:
	uv run python -m scripts.workflow.cli full $(filter-out $@,$(MAKECMDGOALS))

# Faz push de commits e tags com argumentos opcionais
push:
	uv run python -m scripts.workflow.cli push $(filter-out $@,$(MAKECMDGOALS))

# Cria uma tag de release com argumentos opcionais
release:
	uv run python -m scripts.workflow.cli release $(filter-out $@,$(MAKECMDGOALS))

# Gerencia tags (listar, criar, deletar) com argumentos opcionais
tag:
	uv run python -m scripts.workflow.cli tag $(filter-out $@,$(MAKECMDGOALS))

# Exibe informações de versão do projeto
version:
	uv run python -m scripts.workflow.cli version $(filter-out $@,$(MAKECMDGOALS))

# Executa o fluxo completo de deployment (check + push + release) com argumentos
deploy:
	uv run python -m scripts.workflow.cli deploy $(filter-out $@,$(MAKECMDGOALS))

# Gerencia configurações do workflow (env path, target path, etc)
config:
	uv run python -m scripts.workflow.cli config $(filter-out $@,$(MAKECMDGOALS))

# ==================================================================================
# Workflow Shortcuts (for convenience)
# ==================================================================================

# Executa verificações com Ruff e aplica correções automáticas
check-fix:
	uv run python -m scripts.workflow.cli check --fix

# Executa todas as verificações com correções automáticas
full-fix:
	uv run python -m scripts.workflow.cli full --fix

# Faz push forçado pulando validações
push-force:
	uv run python -m scripts.workflow.cli push --force --no-validate

# Faz push apenas das tags (sem commits)
push-tags:
	uv run python -m scripts.workflow.cli push --tags-only

# Cria uma tag de release e faz push
release-push:
	uv run python -m scripts.workflow.cli release --push

# Cria uma tag de release, faz push forçado (sobrescreve tag existente)
release-force:
	uv run python -m scripts.workflow.cli release --push --force

# Lista as tags recentes do projeto
tag-list:
	uv run python -m scripts.workflow.cli tag list

# Cria uma nova tag localmente
tag-create:
	uv run python -m scripts.workflow.cli tag create

# Cria uma nova tag e faz push
tag-create-push:
	uv run python -m scripts.workflow.cli tag create --push

# Cria uma tag e faz push forçado (sobrescreve tag existente)
tag-create-force:
	uv run python -m scripts.workflow.cli tag create --push --force

# Catch-all target para permitir passar argumentos aos comandos
%:
	@:

# ==================================================================================
# Pyright Commands
# ==================================================================================

# Instala Pyright globalmente via npm
pyright-install:
	@echo "📦 Installing Pyright globally via npm..."
	npm install -g pyright
	@echo "✅ Pyright installed successfully!"

# Executa verificação estática de tipos com Pyright
pyright:
	@echo "🔍 Running Pyright static type checking..."
	@if command -v pyright >/dev/null 2>&1; then \
		pyright; \
	else \
		echo "❌ Pyright not found. Install it first with: make pyright-install"; \
		echo "   Or install via npm: npm install -g pyright"; \
		exit 1; \
	fi
