# pyright: reportMissingParameterType=false, reportInconsistentConstructor=false, reportIncompatibleMethodOverride=false
# ruff: noqa: ARG002
"""Testes completos para sistema de erros com 100% de cobertura.

Usa pytest parametrize extensivamente para cobrir todos os casos,
incluindo edge cases e combinações de parâmetros.

Estes testes não precisam de banco de dados - são testes unitários puros.
"""

from __future__ import annotations

import pytest
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from pydantic import BaseModel, Field, ValidationError

from .. import container, exceptions, to_errors, types

# Desabilita banco de dados para estes testes (não precisam de DB)
# Usa marcador 'unit' para desabilitar configuração automática de banco de dados
pytestmark = pytest.mark.unit

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def empty_errors() -> container.Errors:
    """container.Errors vazio."""
    return container.Errors(root=[])


@pytest.fixture
def sample_errors() -> container.Errors:
    """container.Errors com dados de exemplo."""
    return container.Errors(
        root=[
            types.ErrorItem(message="Erro 1", field="email", code=400),
            types.ErrorItem(message="Erro 2", field="name", code=400),
            types.ErrorItem(message="Erro 3", code=500, meta={"trace": "..."}),
        ]
    )


@pytest.fixture
def validation_error() -> ValidationError:
    """ValidationError do Pydantic para testes."""

    class User(BaseModel):
        name: str = Field(min_length=3)
        email: str
        age: int = Field(ge=18)

    try:
        User(name="Ab", email="", age=15)
    except ValidationError as e:
        return e
    raise AssertionError("ValidationError não foi gerado")


# ============================================================================
# types.ErrorItem Tests
# ============================================================================


class TestErrorItem:
    """Testes para types.ErrorItem."""

    @pytest.mark.parametrize(
        ("message", "field", "code", "item", "meta"),
        [
            ("Erro simples", None, None, None, {}),
            ("Erro completo", "email", 400, 0, {"key": "value"}),
            ("Erro sem campo", None, 500, None, {}),
            ("Erro sem código", "name", None, None, {}),
        ],
    )
    def test_create(self, message, field, code, item, meta):
        """Criação de types.ErrorItem com diferentes combinações."""
        item_obj = types.ErrorItem(message=message, field=field, code=code, item=item, meta=meta)
        assert item_obj.message == message
        assert item_obj.field == field
        assert item_obj.code == code
        assert item_obj.item == item
        assert item_obj.meta == meta

    @pytest.mark.parametrize(
        ("exclude_unset", "exclude_none", "expected_keys"),
        [
            (True, True, {"message"}),  # exclude_unset=True, exclude_none=True → apenas message
            (
                False,
                True,
                {"message", "meta"},
            ),  # exclude_unset=False, exclude_none=True → message + meta (field/code/item são None)
            (
                True,
                False,
                {"message", "field", "code"},
            ),  # exclude_unset=True, exclude_none=False → campos definidos (meta não é incluído porque tem default_factory)
            (
                False,
                False,
                {"message", "field", "code", "item", "meta"},
            ),  # exclude_unset=False, exclude_none=False → todos campos
        ],
    )
    def test_model_dump(self, exclude_unset, exclude_none, expected_keys):
        """Serialização com diferentes opções."""
        item = types.ErrorItem(message="Test", field=None, code=None)
        dump = item.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none)
        assert set(dump.keys()) == expected_keys


# ============================================================================
# container.Errors Tests
# ============================================================================


class TestErrors:
    """Testes para container.Errors container."""

    def test_add_string(self, empty_errors):
        """Adiciona erro como string."""
        empty_errors.add("Erro teste")
        assert len(empty_errors) == 1
        assert empty_errors.root[0].message == "Erro teste"

    def test_add_error_item(self, empty_errors):
        """Adiciona types.ErrorItem diretamente."""
        item = types.ErrorItem(message="Item direto", code=400)
        empty_errors.add(item)
        assert len(empty_errors) == 1
        assert empty_errors.root[0] is item

    @pytest.mark.parametrize(
        ("message", "field", "code", "item", "meta"),
        [
            ("Erro", None, None, None, {}),
            ("Erro", "email", None, None, {}),
            ("Erro", None, 400, None, {}),
            ("Erro", "email", 400, 0, {"key": "value"}),
        ],
    )
    def test_add_with_params(self, empty_errors, message, field, code, item, meta):
        """Adiciona erro com parâmetros opcionais."""
        empty_errors.add(message, field=field, code=code, item=item, **meta)
        assert len(empty_errors) == 1
        assert empty_errors.root[0].message == message
        assert empty_errors.root[0].field == field
        assert empty_errors.root[0].code == code
        assert empty_errors.root[0].item == item

    def test_extend(self, empty_errors):
        """Adiciona múltiplos erros."""
        empty_errors.extend(["Erro 1", "Erro 2", types.ErrorItem(message="Erro 3")])
        assert len(empty_errors) == 3

    def test_bool_empty(self, empty_errors):
        """Verificação booleana com container.Errors vazio."""
        assert not empty_errors

    def test_bool_with_errors(self, sample_errors):
        """Verificação booleana com erros."""
        assert sample_errors

    def test_len(self, sample_errors):
        """Quantidade de erros."""
        assert len(sample_errors) == 3

    def test_iter(self, sample_errors):
        """Iteração sobre erros."""
        items = list(sample_errors)
        assert len(items) == 3
        assert all(isinstance(item, types.ErrorItem) for item in items)

    def test_add_operator(self, sample_errors):
        """Operador + combina container.Errors."""
        other = container.Errors(root=[types.ErrorItem(message="Novo erro")])
        result = sample_errors + other
        assert len(result) == 4
        assert len(sample_errors) == 3  # Original não modificado

    def test_sub_operator(self, sample_errors):
        """Operador - remove erros."""
        to_remove = container.Errors(root=[sample_errors.root[0]])
        result = sample_errors - to_remove
        assert len(result) == 2

    def test_messages_property(self, sample_errors):
        """Lista de mensagens."""
        messages = sample_errors.messages
        assert messages == ["Erro 1", "Erro 2", "Erro 3"]

    @pytest.mark.parametrize(
        ("default_code", "expected_codes"),
        [
            (500, [400, 400, 500]),  # Códigos explícitos mantidos
            (200, [400, 400, 500]),  # Códigos explícitos mantidos
        ],
    )
    def test_normalize_codes_with_explicit(self, sample_errors, default_code, expected_codes):
        """Normaliza códigos respeitando valores explícitos."""
        sample_errors.normalize_codes(default_code)
        assert [e.code for e in sample_errors.root] == expected_codes

    def test_normalize_codes_without_explicit(self, empty_errors):
        """Normaliza códigos quando não há códigos explícitos."""
        empty_errors.add("Erro 1")
        empty_errors.add("Erro 2", code=None)
        empty_errors.normalize_codes(500)
        assert all(e.code == 500 for e in empty_errors.root)

    @pytest.mark.parametrize(
        ("field", "code", "has_meta", "expected_count"),
        [
            (None, None, None, 3),
            ("email", None, None, 1),
            (None, 400, None, 2),
            (None, None, True, 1),
            (None, None, False, 2),
            ("email", 400, None, 1),
            (None, 500, True, 1),
        ],
    )
    def test_filter_by(self, sample_errors, field, code, has_meta, expected_count):
        """Filtra erros por critérios."""
        filtered = sample_errors.filter_by(field=field, code=code, has_meta=has_meta)
        assert len(filtered) == expected_count

    def test_merge(self, empty_errors, sample_errors):
        """Mescla container.Errors."""
        empty_errors.merge(sample_errors)
        assert len(empty_errors) == 3

    @pytest.mark.parametrize(
        ("exclude_unset", "exclude_none", "expected_structure"),
        [
            (True, True, {"description", "data"}),
            (False, False, {"description", "data"}),
        ],
    )
    def test_to_dict(self, sample_errors, exclude_unset, exclude_none, expected_structure):
        """Serialização para dict."""
        result = sample_errors.to_dict(exclude_unset=exclude_unset, exclude_none=exclude_none)
        assert set(result.keys()) == expected_structure
        assert len(result["description"]) == 3
        assert len(result["data"]) == 3


# ============================================================================
# container.Errors.normalize Tests - Cobertura Completa
# ============================================================================


class TestErrorsNormalize:
    """Testes para container.Errors.normalize cobrindo todos os tipos."""

    def test_normalize_errors(self, sample_errors):
        """Normaliza container.Errors (idempotente)."""
        result = container.Errors.normalize(sample_errors)
        assert result is sample_errors

    def test_normalize_error_item(self):
        """Normaliza types.ErrorItem."""
        item = types.ErrorItem(message="Item", code=400)
        result = container.Errors.normalize(item)
        assert len(result) == 1
        assert result.root[0] is item

    def test_normalize_api_error(self):
        """Normaliza exceptions.ApiError."""
        api_error = exceptions.ApiError("Erro")
        result = container.Errors.normalize(api_error)
        assert len(result) == 1

    def test_normalize_validation_error_pydantic(self, validation_error):
        """Normaliza ValidationError do Pydantic."""
        result = container.Errors.normalize(validation_error)
        assert len(result) >= 2  # Pelo menos name e age
        assert all(e.field for e in result.root)

    def test_normalize_validation_error_ninja(self):
        """Normaliza ValidationError do Ninja."""
        ninja_error = NinjaValidationError([{"loc": ("field",), "msg": "Erro", "type": "error"}])
        result = container.Errors.normalize(ninja_error)
        assert len(result) == 1

    def test_normalize_validation_error_empty(self):
        """ValidationError sem erros."""

        # Cria um ValidationError mock sem erros
        class EmptyError(ValidationError):
            def __new__(cls):
                # ValidationError usa __new__ em vez de __init__
                return super().__new__(cls, "Validation error", [])

            def errors(
                self,
                include_url: bool = True,
                include_context: bool = False,
                include_input: bool = True,
            ):
                return []

        error = EmptyError()
        result = container.Errors.normalize(error)
        assert len(result) == 1
        # ValidationError sem erros retorna mensagem "0 validation errors for ..."
        assert "validation error" in result.messages[0].lower()

    @pytest.mark.parametrize(
        "http_error_args",
        [
            (400, "mensagem"),
            (400, {"msg": "erro"}),
            (400, 123),  # Não é str nem dict
        ],
    )
    def test_normalize_http_error(self, http_error_args):
        """Normaliza HttpError em diferentes formatos."""
        # HttpError precisa de status_code e message
        error = HttpError(*http_error_args)
        result = container.Errors.normalize(error)
        assert len(result) >= 1

    @pytest.mark.parametrize(
        ("error_dict", "code", "expected_field", "expected_count"),
        [
            ({"description": ["Erro 1", "Erro 2"], "data": []}, None, None, 0),  # data vazio
            ({"description": "Erro único"}, None, None, 1),
            ({"description": ["Erro 1", "Erro 2"]}, None, None, 2),
            ({"message": "Erro", "field": "email"}, None, "email", 1),
            ({"message": "Erro", "code": 400}, 500, None, 1),  # Code explícito tem prioridade
            ({"msg": "Erro"}, 500, None, 1),  # Usa fallback
            ({"message": "Erro", "meta": {"key": "value"}}, None, None, 1),
        ],
    )
    def test_normalize_dict(self, error_dict, code, expected_field, expected_count):
        """Normaliza dict em diferentes formatos."""
        result = container.Errors.normalize(error_dict, code=code)
        assert len(result) == expected_count
        if expected_field and len(result) > 0:
            assert result.root[0].field == expected_field

    def test_normalize_dict_with_meta_explicit(self):
        """Dict com meta explícito."""
        error_dict = {"message": "Erro", "meta": {"key": "value"}}
        result = container.Errors.normalize(error_dict)
        assert result.root[0].meta == {"key": "value"}

    def test_normalize_dict_with_meta_implicit(self):
        """Dict com campos extras como meta."""
        error_dict = {"message": "Erro", "extra1": "value1", "extra2": "value2"}
        result = container.Errors.normalize(error_dict)
        assert "extra1" in result.root[0].meta
        assert "extra2" in result.root[0].meta

    @pytest.mark.parametrize(
        ("sequence", "code", "expected_count"),
        [
            (["Erro 1", "Erro 2"], None, 2),
            (("Erro 1", "Erro 2"), None, 2),
            ([types.ErrorItem(message="Item")], None, 1),
            ([{"message": "Erro"}], None, 1),
            ([ValueError("Erro")], None, 1),
            ([1, "texto", 255], None, 3),
        ],
    )
    def test_normalize_sequence(self, sequence, code, expected_count):
        """Normaliza sequências (lista/tuple)."""
        result = container.Errors.normalize(sequence, code=code)
        assert len(result) == expected_count

    def test_normalize_sequence_with_errors(self, sample_errors):
        """Sequência contendo container.Errors."""
        result = container.Errors.normalize([sample_errors])
        assert len(result) == 3

    def test_normalize_sequence_with_api_error(self):
        """Sequência contendo exceptions.ApiError."""
        api_error = exceptions.ApiError("Erro")
        result = container.Errors.normalize([api_error])
        assert len(result) == 1

    def test_normalize_sequence_with_validation_error(self, validation_error):
        """Sequência contendo ValidationError."""
        result = container.Errors.normalize([validation_error, "outro erro"])
        assert len(result) >= 3  # ValidationError expandido + outro erro

    def test_normalize_sequence_with_http_error(self):
        """Sequência contendo HttpError."""
        http_error = HttpError(400, "Erro HTTP")
        result = container.Errors.normalize([http_error])
        assert len(result) >= 1

    def test_normalize_exception(self):
        """Normaliza Exception genérica."""
        result = container.Errors.normalize(ValueError("Erro"))
        assert len(result) == 1
        assert result.root[0].message == "Erro"

    def test_normalize_exception_with_code(self):
        """Exception com código."""
        result = container.Errors.normalize(ValueError("Erro"), code=500)
        assert result.root[0].code == 500

    def test_normalize_fallback(self):
        """Fallback para qualquer outro tipo."""
        result = container.Errors.normalize(12345)
        assert len(result) == 1
        assert result.root[0].message == "12345"

    def test_normalize_fallback_with_code(self):
        """Fallback com código."""
        result = container.Errors.normalize(12345, code=400)
        assert result.root[0].code == 400


# ============================================================================
# exceptions.ApiError Tests
# ============================================================================


class TestApiError:
    """Testes para exceptions.ApiError exception."""

    @pytest.mark.parametrize(
        ("error_input", "code"),
        [
            ("Erro string", None),
            ({"message": "Erro"}, None),
            ({"message": "Erro"}, 400),
            (types.ErrorItem(message="Item"), None),
            (container.Errors(root=[types.ErrorItem(message="Erro")]), None),
            (ValueError("Erro"), None),
        ],
    )
    def test_init(self, error_input, code):
        """Inicialização com diferentes tipos."""
        api_error = exceptions.ApiError(error_input, code=code)
        assert len(api_error.errors) >= 1

    def test_errors_property(self):
        """Acessa container.Errors interno."""
        api_error = exceptions.ApiError("Erro")
        assert isinstance(api_error.errors, container.Errors)

    def test_message_property(self):
        """Primeira mensagem."""
        api_error = exceptions.ApiError("Erro teste")
        assert api_error.message == "Erro teste"

    def test_message_property_empty(self):
        """Mensagem quando vazio."""
        api_error = exceptions.ApiError(container.Errors(root=[]))
        assert api_error.message == "exceptions.ApiError"

    def test_str(self):
        """Representação string."""
        api_error = exceptions.ApiError("Erro teste")
        assert str(api_error) == "Erro teste"

    def test_inheritance(self):
        """Herança funciona."""

        class UserError(exceptions.ApiError):
            pass

        error = UserError("Erro de usuário")
        assert isinstance(error, exceptions.ApiError)
        assert len(error.errors) == 1


# ============================================================================
# to_errors Tests
# ============================================================================


class TestToErrors:
    """Testes para função to_errors."""

    def test_to_errors_alias(self):
        """to_errors é alias para container.Errors.normalize."""
        result1 = to_errors("Erro")
        result2 = container.Errors.normalize("Erro")
        assert len(result1) == len(result2)
        assert result1.messages == result2.messages

    @pytest.mark.parametrize(
        ("error_input", "code"),
        [
            ("Erro", None),
            (["Erro 1", "Erro 2"], None),
            ({"message": "Erro"}, 400),
            (ValueError("Erro"), 500),
        ],
    )
    def test_to_errors_various_types(self, error_input, code):
        """Converte vários tipos."""
        result = to_errors(error_input, code=code)
        assert isinstance(result, container.Errors)
        assert len(result) >= 1


# ============================================================================
# Edge Cases e Combinações Complexas
# ============================================================================


class TestEdgeCases:
    """Testes para edge cases e combinações complexas."""

    def test_lista_mista_completa(self, validation_error):
        """Lista mista com todos os tipos possíveis."""
        errors = container.Errors(root=[])
        # Adiciona lista mista usando normalize e merge
        mixed_list = [
            1,
            "texto",
            255,
            {"message": "dict", "field": "email"},
            types.ErrorItem(message="item", code=400),
            container.Errors(root=[types.ErrorItem(message="errors")]),
            exceptions.ApiError("api error"),
            validation_error,
            HttpError(400, "http error"),
            ValueError("exception"),
        ]
        normalized = container.Errors.normalize(mixed_list)
        errors.merge(normalized)
        assert len(errors) >= 10

    def test_dict_code_zero(self):
        """Dict com code=0 (deve ser respeitado)."""
        result = container.Errors.normalize({"message": "Erro", "code": 0}, code=500)
        assert result.root[0].code == 0

    def test_dict_code_none_explicit(self):
        """Dict com code=None explícito."""
        result = container.Errors.normalize({"message": "Erro", "code": None}, code=500)
        assert result.root[0].code is None

    def test_dict_meta_not_dict(self):
        """Dict com meta que não é dict."""
        result = container.Errors.normalize({"message": "Erro", "meta": "não é dict"})
        assert result.root[0].meta == {}

    def test_validation_error_without_msg(self):
        """ValidationError com erro sem msg."""

        class CustomError(ValidationError):
            def __new__(cls):
                # ValidationError usa __new__ em vez de __init__
                return super().__new__(cls, "Validation error", [])

            def errors(
                self,
                include_url: bool = True,
                include_context: bool = False,
                include_input: bool = True,
            ):
                return [{"loc": ("field",), "type": "error"}]  # Sem "msg"

        error = CustomError()
        result = container.Errors.normalize(error)
        # Deve filtrar erros sem msg
        assert len(result) == 0 or all(e.message for e in result.root)

    def test_http_error_empty_args(self):
        """HttpError sem args."""

        class EmptyHttpError(HttpError):
            def __init__(self):
                # HttpError precisa de status_code e message
                super().__init__(400, "")

        error = EmptyHttpError()
        result = container.Errors.normalize(error)
        assert len(result) >= 1

    def test_sequence_empty(self):
        """Sequência vazia."""
        result = container.Errors.normalize([])
        assert len(result) == 0

    def test_sequence_nested(self):
        """Sequência aninhada."""
        result = container.Errors.normalize([["Erro 1"], ["Erro 2"]])
        # Cada lista interna é tratada como item único
        assert len(result) == 2

    def test_filter_by_all_none(self, sample_errors):
        """Filtro com todos parâmetros None."""
        filtered = sample_errors.filter_by()
        assert len(filtered) == 3

    def test_normalize_codes_all_explicit(self):
        """Normaliza quando todos têm código explícito."""
        errors = container.Errors(
            root=[
                types.ErrorItem(message="Erro 1", code=400),
                types.ErrorItem(message="Erro 2", code=401),
            ]
        )
        errors.normalize_codes(500)
        assert errors.root[0].code == 400
        assert errors.root[1].code == 401

    def test_merge_empty(self, sample_errors):
        """Mescla container.Errors vazio."""
        empty = container.Errors(root=[])
        sample_errors.merge(empty)
        assert len(sample_errors) == 3

    def test_sub_operator_no_match(self, sample_errors):
        """Subtração sem matches."""
        other = container.Errors(root=[types.ErrorItem(message="Não existe")])
        result = sample_errors - other
        assert len(result) == 3

    def test_to_dict_empty_errors(self):
        """Serialização de container.Errors vazio."""
        errors = container.Errors(root=[])
        result = errors.to_dict()
        assert result == {"description": [], "data": []}

    def test_to_dict_exclude_unset_false(self):
        """Serialização sem exclude_unset."""
        errors = container.Errors(root=[types.ErrorItem(message="Erro", field="email")])
        result = errors.to_dict(exclude_unset=False, exclude_none=True)
        assert "field" in result["data"][0]

    def test_to_dict_exclude_none_false(self):
        """Serialização sem exclude_none."""
        errors = container.Errors(root=[types.ErrorItem(message="Erro", field=None)])
        result = errors.to_dict(exclude_unset=True, exclude_none=False)
        assert "field" in result["data"][0]
