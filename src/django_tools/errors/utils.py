"""Utilitários para sistema de erros.

Funções puras e reutilizáveis para manipulação de erros e respostas.
Desacopladas dos módulos principais para evitar redundância.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ninja.errors import HttpError


def has_significant_data(data: Any) -> bool:
    """Verifica se há dados significativos (não None, não vazio).

    Args:
        data: Dados a serem verificados

    Returns:
        True se há dados significativos, False caso contrário

    Examples:
        >>> has_significant_data(None)
        False
        >>> has_significant_data("")
        False
        >>> has_significant_data([])
        False
        >>> has_significant_data("texto")
        True
        >>> has_significant_data([1, 2, 3])
        True

    """
    if data is None:
        return False
    if isinstance(data, (str, bytes)):
        return bool(data)
    if isinstance(data, (list, dict, set)):
        return bool(data)
    return True


def detect_response_type(
    has_error: bool,
    has_data: bool,
) -> Literal["success", "error", "partial"]:
    """Detecta tipo de resposta baseado em presença de erros e dados.

    Args:
        has_error: Se há erros
        has_data: Se há dados

    Returns:
        Tipo de resposta: "success", "error" ou "partial"

    Examples:
        >>> detect_response_type(False, True)
        'success'
        >>> detect_response_type(True, False)
        'error'
        >>> detect_response_type(True, True)
        'partial'

    """
    if has_error and has_data:
        return "partial"
    if has_error:
        return "error"
    return "success"


def normalize_http_status(cod: int | None, default: int = HTTPStatus.OK) -> int:
    """Normaliza HTTP status baseado no código de corpo.

    Args:
        cod: Código de corpo da resposta
        default: Valor default se não for código especial

    Returns:
        HTTP status code normalizado

    Examples:
        >>> normalize_http_status(500)
        500
        >>> normalize_http_status(200)
        200
        >>> normalize_http_status(None)
        200

    """
    if cod == 500:
        return int(HTTPStatus.INTERNAL_SERVER_ERROR)
    return int(default)


def serialize_error_to_payload(error: Any) -> dict[str, Any] | None:
    """Serializa erro para payload de resposta.

    Aceita múltiplos tipos de erro e normaliza para dict.
    Se o erro já for Errors ou ErrorItem, chama to_dict().

    Args:
        error: Erro a ser serializado (Errors, ErrorItem, dict, None, etc.)

    Returns:
        Dict com payload do erro ou None

    Examples:
        >>> serialize_error_to_payload(None)
        None
        >>> serialize_error_to_payload({"message": "erro"})
        {"message": "erro"}

    """
    from .container import Errors
    from .types import ErrorItem

    if error is None:
        return None

    if isinstance(error, Errors):
        return error.to_dict()
    if isinstance(error, ErrorItem):
        return Errors(root=[error]).to_dict()
    # Já é dict ou outro tipo serializável
    return error


def extract_http_error_payload(exc: HttpError) -> dict[str, Any] | str:
    """Extrai payload de HttpError em diferentes formatos.

    Função pura e reutilizável para extrair payload de HttpError do Ninja.
    Suporta múltiplos formatos de construção do HttpError.

    Args:
        exc: HttpError do Ninja

    Returns:
        Payload extraído (dict, str ou outro tipo convertido para str)

    Examples:
        >>> extract_http_error_payload(HttpError(400, "mensagem"))
        'mensagem'
        >>> extract_http_error_payload(HttpError(400, {"msg": "erro"}))
        {'msg': 'erro'}
        >>> extract_http_error_payload(HttpError({"msg": "erro"}))
        {'msg': 'erro'}
        >>> extract_http_error_payload(HttpError("mensagem"))
        'mensagem'

    """
    if len(exc.args) > 1:
        return exc.args[1] if isinstance(exc.args[1], (str, dict)) else str(exc.args[1])
    if exc.args and isinstance(exc.args[0], dict):
        return exc.args[0]
    return str(exc.args[0]) if exc.args else str(exc)
