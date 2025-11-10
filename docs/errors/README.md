# Error System - Estrutura Modular

Este módulo fornece um sistema de erros padronizado e reutilizável para APIs Django/Ninja, projetado para ser **desacoplado do Django** e funcionar standalone quando necessário.

## Visão Geral

O sistema de erros permite normalizar, manipular e serializar erros de diferentes fontes (strings, dicionários, exceções, ValidationError, HttpError, etc.) em uma estrutura padronizada.

## Arquitetura

A estrutura foi projetada para **evitar circular imports** e manter o código **desacoplado do Django/Ninja** até o momento de uso real.

### Hierarquia de Dependências

```text
Camada 0: types.py          → ErrorItem (tipos básicos, sem dependências internas)
Camada 1: mixins.py         → NormalizeErrorsMixin (lógica de conversão)
Camada 2: container.py      → Errors (container + operações)
Camada 3: exceptions.py     → ApiError (exceções customizadas)
Camada 3: utils.py          → Funções auxiliares (serialize, extract, etc.)
Camada 4: __init__.py       → API pública (ErrorItem, Errors, ApiError, to_errors)
```

**Regra fundamental**: Cada módulo só importa de camadas inferiores, evitando dependências circulares.

### Imports Lazy e Opcionais

Para evitar forçar a inicialização do Django quando não necessário, usamos:

1. **Duck typing** para verificar tipos Ninja sem importá-los:

   ```python
   def _is_http_error(obj: Any) -> bool:
       return type(obj).__name__ == "HttpError" and type(obj).__module__ == "ninja.errors"
   ```

2. **Imports dentro de funções** quando necessário:

   ```python
   def normalize(cls, error: Any, code: int | None = None):
       from .container import Errors  # Import tardio evita ciclo
       ...
   ```

3. **TYPE_CHECKING** para type hints sem imports em runtime:

   ```python
   if TYPE_CHECKING:
       from .container import Errors
   ```

## Estrutura de Arquivos

```text
src/django_tools/errors/
├── __init__.py          # API pública (ErrorItem, Errors, ApiError, to_errors)
├── types.py            # ErrorItem (tipo básico, sem dependências internas)
├── mixins.py           # NormalizeErrorsMixin (lógica de conversão de erros)
├── container.py        # Errors (container com operações: add, filter, merge, etc.)
├── exceptions.py        # ApiError (exceção base para APIs)
├── utils.py            # Funções auxiliares (serialize_error_to_payload, extract_http_error_payload, etc.)
└── tests/              # Testes unitários (98 testes)
    ├── __init__.py
    └── test_errors.py
```

## Uso

### Import básico (sem Django)

O módulo funciona completamente standalone, sem necessidade de inicializar Django:

```python
from django_tools.errors import ErrorItem, Errors, ApiError, to_errors

# Conversão direta de string
errors = to_errors("simple error")
print(errors.messages)  # ['simple error']

# Criação manual de ErrorItem
item = ErrorItem(message="Campo inválido", field="email", code=400)
print(item.message)  # 'Campo inválido'

# Container Errors com operações
errors = Errors(root=[])
errors.add("Erro 1")
errors.add("Erro 2", field="name", code=400)
print(len(errors))  # 2
print(errors.messages)  # ['Erro 1', 'Erro 2']
```

### Normalização de diferentes tipos

```python
from django_tools.errors import Errors, to_errors

# String
errors = Errors.normalize("error")
print(errors.messages)  # ['error']

# Lista de strings
errors = Errors.normalize(["error1", "error2"])
print(len(errors))  # 2

# Dicionário
errors = Errors.normalize({"message": "error", "field": "email", "code": 400})
print(errors.errors[0].field)  # 'email'

# Lista heterogênea
errors = Errors.normalize([
    "string error",
    {"message": "dict error", "field": "name"},
    ErrorItem(message="item error", code=500),
    ValueError("exception error")
])
print(len(errors))  # 4
```

### Normalização com ValidationError (Pydantic)

```python
from pydantic import BaseModel, ValidationError
from django_tools.errors import Errors

class User(BaseModel):
    name: str
    age: int

try:
    User(name='John', age='invalid')
except ValidationError as e:
    errors = Errors.normalize(e)
    print(errors.messages)
    # ['Input should be a valid integer, unable to parse string as an integer']
    print(errors.errors[0].field)  # 'age'
```

### Operações no container Errors

```python
from django_tools.errors import Errors, ErrorItem

errors = Errors(root=[])
errors.add("Erro 1", field="email", code=400)
errors.add("Erro 2", field="name", code=400)
errors.add("Erro 3", field="email", code=500)

# Filtrar por campo
email_errors = errors.filter_by(field="email")
print(len(email_errors))  # 2

# Filtrar por código
code_400_errors = errors.filter_by(code=400)
print(len(code_400_errors))  # 2

# Normalizar códigos
errors.normalize_codes(default_code=400)
print(all(e.code == 400 for e in errors))  # True

# Operações de conjunto
errors1 = Errors(root=[ErrorItem(message="e1")])
errors2 = Errors(root=[ErrorItem(message="e2")])
combined = errors1 + errors2
print(len(combined))  # 2
```

### Exceções customizadas (ApiError)

```python
from django_tools.errors import ApiError, Errors

# Criar exceção com string
raise ApiError("Erro de negócio")

# Criar exceção com dicionário
raise ApiError({"message": "Erro", "field": "email"}, code=400)

# Criar exceção com Errors
errors = Errors(root=[ErrorItem(message="Erro", field="email")])
raise ApiError(errors)

# Exceção customizada
class UserError(ApiError):
    pass

raise UserError("Usuário inválido")
```

### Com Django/Ninja (import lazy)

O Ninja só é importado quando realmente necessário, evitando forçar a inicialização do Django:

```python
from django_tools.errors import Errors

# Em um endpoint Django Ninja
from ninja.errors import HttpError

try:
    raise HttpError(400, {"message": "error"})
except HttpError as e:
    # Ninja é importado aqui, não no import do módulo
    errors = Errors.normalize(e)
    print(errors.messages)
```

## Testes

O módulo possui cobertura completa de testes (98 testes) cobrindo:

- Criação e manipulação de `ErrorItem`
- Operações do container `Errors` (add, filter, merge, filter_by)
- Normalização de todos os tipos suportados (string, dict, list, Exception, ValidationError, HttpError)
- Exceções `ApiError` e herança
- Função `to_errors()` e seus aliases
- Casos extremos e edge cases

Para rodar os testes:

```bash
pytest src/django_tools/errors/tests/test_errors.py -v
```

## Benefícios

✅ **Sem circular imports**: hierarquia clara de dependências em camadas  
✅ **Desacoplado do Django**: funciona completamente standalone  
✅ **Imports opcionais**: Ninja/Django só quando necessário (lazy imports)  
✅ **Testável**: 98 testes passando com cobertura completa  
✅ **Type-safe**: tipos completos com duck typing e TYPE_CHECKING  
✅ **Extensível**: fácil adicionar novos conversores de erro  
✅ **Performático**: imports tardios evitam overhead desnecessário  
✅ **Reutilizável**: pode ser usado em qualquer projeto Python, não apenas Django  

## Warnings do Linter

Os warnings de "Cycle detected" são **esperados e resolvidos em runtime** através dos imports tardios dentro das funções. Isso é uma prática comum e aceitável para resolver dependências circulares em Python quando a hierarquia de camadas não é suficiente.

O código usa `# pyright: ignore[reportImportCycles]` em `container.py` para documentar que o ciclo é intencional e resolvido em runtime.

## Componentes Principais

### ErrorItem

Estrutura básica de um erro com campos opcionais:

- `message`: Mensagem do erro (obrigatório)
- `field`: Campo relacionado (opcional)
- `code`: Código do erro (opcional)
- `item`: Índice/identificador (opcional)
- `meta`: Metadados adicionais (opcional)

### Errors

Container rico com operações:

- `normalize()`: Converte qualquer tipo de erro para Errors
- `add()`: Adiciona um erro ao container
- `filter_by()`: Filtra erros por critérios
- `normalize_codes()`: Normaliza códigos de erro
- `merge()`: Mescla outro Errors
- `to_dict()`: Serializa para dicionário

### ApiError

Exceção base que carrega Errors internamente:

- Aceita qualquer tipo de erro e normaliza automaticamente
- Pode ser estendida para exceções de domínio específico
- Propriedade `errors` retorna o container Errors
- Propriedade `message` retorna a primeira mensagem ou nome da classe

### to_errors()

Função de conveniência que é um alias para `Errors.normalize()`:

- Interface simplificada para conversão direta
- Útil para casos simples onde não precisa manipular o container
