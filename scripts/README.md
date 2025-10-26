# Workflow Automation System

Sistema modular de automação para qualidade de código e gerenciamento de releases.

## Visão Geral

O sistema de workflow é sua **central de comando** para garantir qualidade de código antes de fazer push. Ele integra validações (Ruff, Pyright, testes) com operações Git (push, tags, releases) de forma modular e extensível.

## Instalação

Todas as dependências estão incluídas no `pyproject.toml`:

```bash
uv sync --dev
```

## Arquitetura

```
scripts/workflow/
├── cli.py              # Interface CLI principal
├── core/               # Componentes centrais
│   ├── models.py       # CommandResult, JobResult
│   └── runner.py       # WorkflowRunner
├── commands/           # Comandos modulares
│   ├── check.py        # Validações (ruff, pyright, tests)
│   ├── push.py         # Operações de push
│   ├── tag.py          # Gerenciamento de tags
│   └── version.py      # Informações de versão
└── utils/              # Utilitários
    └── git.py          # Funções Git
```

## Uso via Makefile (Recomendado)

### Comandos de Validação

```bash
# Verificação rápida (apenas Ruff)
make check

# Verificação rápida com auto-fix
make check-fix

# Verificação completa (Ruff + Pyright + Testes)
make full

# Verificação completa com auto-fix
make full-fix
```

### Comandos de Push

```bash
# Push com validação automática
make push

# Push forçado (sem validação - use com cuidado!)
make push-force

# Push apenas tags
make push-tags
```

### Comandos de Release

```bash
# Criar tag de release (valida antes)
make release

# Criar tag e fazer push imediatamente
make release-push
```

### Comandos de Tag

```bash
# Listar tags recentes
make tag-list

# Criar tag manualmente
make tag-create

# Criar tag e fazer push
make tag-create-push
```

### Comandos Utilitários

```bash
# Mostrar versão atual e próximas versões
make version

# Deploy completo (validação + push tudo)
make deploy
```

## Uso via CLI Direto

### Validações

```bash
# Apenas Ruff
uv run python -m scripts.workflow.cli check

# Ruff com auto-fix
uv run python -m scripts.workflow.cli check --fix

# Adicionar Pyright
uv run python -m scripts.workflow.cli check --pyright

# Adicionar testes
uv run python -m scripts.workflow.cli check --tests

# Tudo junto
uv run python -m scripts.workflow.cli full

# Tudo com auto-fix
uv run python -m scripts.workflow.cli full --fix

# Pular Pyright
uv run python -m scripts.workflow.cli full --skip-pyright

# Pular testes
uv run python -m scripts.workflow.cli full --skip-tests
```

### Push

```bash
# Push com validação
uv run python -m scripts.workflow.cli push

# Push sem validação
uv run python -m scripts.workflow.cli push --no-validate

# Push forçado
uv run python -m scripts.workflow.cli push --force

# Push apenas tags
uv run python -m scripts.workflow.cli push --tags-only
```

### Release

```bash
# Criar tag (valida antes)
uv run python -m scripts.workflow.cli release

# Criar tag e fazer push
uv run python -m scripts.workflow.cli release --push

# Criar tag sem validação
uv run python -m scripts.workflow.cli release --no-validate
```

### Tags

```bash
# Listar tags
uv run python -m scripts.workflow.cli tag list

# Listar mais tags
uv run python -m scripts.workflow.cli tag list --limit 20

# Criar tag
uv run python -m scripts.workflow.cli tag create

# Criar tag e fazer push
uv run python -m scripts.workflow.cli tag create --push

# Deletar tag local
uv run python -m scripts.workflow.cli tag delete --name v1.0.0

# Deletar tag local e remota
uv run python -m scripts.workflow.cli tag delete --name v1.0.0 --remote
```

### Versão

```bash
# Mostrar informações de versão
uv run python -m scripts.workflow.cli version
```

### Deploy

```bash
# Deploy completo (validação + push)
uv run python -m scripts.workflow.cli deploy

# Deploy sem validação (não recomendado)
uv run python -m scripts.workflow.cli deploy --skip-validation
```

## Fluxos de Trabalho Recomendados

### 1. Desenvolvimento Normal

```bash
# Durante desenvolvimento
make check-fix          # Valida e corrige Ruff

# Antes de commitar
make full               # Validação completa

# Após commitar
make push               # Push com validação
```

### 2. Release com Tag

```bash
# 1. Atualizar versão no pyproject.toml manualmente
vim pyproject.toml      # Alterar version = "X.Y.Z"

# 2. Commitar a mudança de versão
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"

# 3. Criar tag e fazer push
make release-push       # Valida, cria tag, e faz push
```

### 3. Deploy Rápido

```bash
# Após commitar suas mudanças
make deploy             # Valida tudo e faz push
```

### 4. Correção Urgente (Hotfix)

```bash
# Validação mínima + push
make check
make push-force         # Pula validação completa
```

## O Que Cada Comando Valida

### `check` (Ruff)
- ✅ Instalação do Ruff
- ✅ Linting (com ou sem auto-fix)
- ✅ Formatação (com ou sem auto-fix)

### `full` (Completo)
- ✅ Ruff (linting + formatação)
- ✅ Pyright (type checking)
- ✅ Pytest (testes com coverage)

### `push` (Push com Validação)
- ✅ Ruff checks
- ✅ Verifica se há commits para push
- ✅ Push de commits
- ✅ Push de tags (se houver)

### `release` (Release com Tag)
- ✅ Validação completa (Ruff + Pyright + Testes)
- ✅ Lê versão do pyproject.toml
- ✅ Cria tag anotada (v{version})
- ✅ Opcionalmente faz push da tag

### `deploy` (Deploy Completo)
- ✅ Validação completa
- ✅ Push de commits
- ✅ Push de tags

## Diferenças do Sistema Antigo

### Antes (`workflow_dryrun.py`)
- Monolítico (um arquivo único)
- Simulava CI/CD localmente
- Release automático no CI/CD

### Agora (Package `workflow`)
- **Modular**: Separação clara de responsabilidades
- **Extensível**: Fácil adicionar novos comandos
- **Controle local**: Releases manuais via CLI
- **CI/CD simplificado**: Apenas testes, sem releases

## Integração com CI/CD

O CI/CD agora é **apenas para validação**:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    - Run Ruff linting
    - Run tests
```

**Releases são feitos localmente** via `make release-push`.

## Troubleshooting

### Script não encontra pyproject.toml

```bash
cd /path/to/django_tools
```

### Testes falhando

```bash
uv run pytest src/ -v
```

### Ruff encontra erros

```bash
make check-fix
```

### Pyright encontra erros

```bash
pyright
# ou
make pyright
```

### Push falha por falta de commits

```bash
# Verifique se há commits para push
git status
git log origin/main..HEAD
```

### Tag já existe

```bash
# Delete a tag local
git tag -d v1.0.0

# Delete a tag remota
git push origin --delete v1.0.0

# Ou use o comando
make tag-list
uv run python -m scripts.workflow.cli tag delete --name v1.0.0 --remote
```

## Comandos Legacy (Ruff direto)

Ainda disponíveis para compatibilidade:

```bash
make ruff-fix           # Ruff format + check --fix
make ruff-check         # Ruff format --check + check
make ruff-format        # Ruff format --check
```

**Recomendação**: Use os novos comandos `make check` e `make full`.

## Dependências

- `typer`: Framework CLI
- `rich`: Visualização rica no terminal
- `pytest`: Framework de testes
- `ruff`: Linter e formatador
- `pyright`: Type checker (opcional)

Todas instaladas automaticamente com `uv sync --dev`.

## Contribuindo

Para adicionar novos comandos:

1. Crie módulo em `scripts/workflow/commands/`
2. Implemente função `{command}_command(project_root, ...)`
3. Exponha em `scripts/workflow/commands/__init__.py`
4. Adicione comando no `cli.py`
5. Adicione atalho no `Makefile`

Exemplo:

```python
# scripts/workflow/commands/mycommand.py
def mycommand_command(project_root: Path) -> bool:
    runner = WorkflowRunner(project_root)
    # ... implementação
    return True
```

```python
# scripts/workflow/cli.py
@app.command()
def mycommand():
    """My custom command."""
    project_root = get_project_root()
    success = mycommand_command(project_root)
    if not success:
        raise typer.Exit(1)
```

```makefile
# Makefile
mycommand:
	uv run python -m scripts.workflow.cli mycommand
```
