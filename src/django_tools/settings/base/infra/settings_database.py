from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Configurações de banco de dados."""

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    url: str | None = Field(
        default=None,
        alias="URL",
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
        description="Complete database URL (e.g., postgresql://user:pass@host:port/db)",
    )
    engine: str = Field(
        default="django.db.backends.sqlite3",
        alias="ENGINE",
        validation_alias=AliasChoices("DATABASE_ENGINE", "DB_ENGINE"),
        description="Database engine",
    )
    name: str = Field(
        default="db.sqlite3",
        alias="NAME",
        validation_alias=AliasChoices("DATABASE_NAME", "DB_NAME"),
        description="Database name",
    )
    user: str | None = Field(
        default=None,
        alias="USER",
        validation_alias=AliasChoices("DATABASE_USER", "DB_USER"),
        description="Database username",
    )
    password: str | None = Field(
        default=None,
        alias="PASSWORD",
        validation_alias=AliasChoices("DATABASE_PASSWORD", "DB_PASSWORD"),
        description="Database password",
    )
    host: str | None = Field(
        default=None,
        alias="HOST",
        validation_alias=AliasChoices("DATABASE_HOST", "DB_HOST"),
        description="Database host",
    )
    port: int | None = Field(
        default=None,
        alias="PORT",
        validation_alias=AliasChoices("DATABASE_PORT", "DB_PORT"),
        description="Database port",
    )
    # Campos avançados do Django para banco de dados
    autocommit: bool = Field(
        default=True,
        alias=("DATABASE_AUTOCOMMIT"),
        validation_alias=AliasChoices("DATABASE_AUTOCOMMIT", "DB_AUTOCOMMIT"),
        description="Habilita autocommit no banco de dados",
    )
    atomic_requests: bool = Field(
        default=False,
        alias="DATABASE_ATOMIC_REQUESTS",
        validation_alias=AliasChoices("DATABASE_ATOMIC_REQUESTS", "DB_ATOMIC_REQUESTS"),
        description="Envolve cada request em uma transação atômica",
    )
    conn_max_age: int = Field(
        default=0,
        alias="DATABASE_CONN_MAX_AGE",
        validation_alias=AliasChoices("DATABASE_CONN_MAX_AGE", "DB_CONN_MAX_AGE"),
        description="Tempo máximo de vida de uma conexão em segundos (0 = sem pool)",
    )
    conn_health_checks: bool | None = Field(
        default=None,
        alias="DATABASE_CONN_HEALTH_CHECKS",
        validation_alias=AliasChoices("DATABASE_CONN_HEALTH_CHECKS", "DB_CONN_HEALTH_CHECKS"),
        description="Habilita verificação de saúde das conexões",
    )
    time_zone: str | None = Field(
        default=None,
        alias="DATABASE_TIME_ZONE",
        validation_alias=AliasChoices("DATABASE_TIME_ZONE", "DB_TIME_ZONE"),
        description="Timezone do banco de dados",
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        alias="DATABASE_OPTIONS",
        validation_alias=AliasChoices("DATABASE_OPTIONS", "DB_OPTIONS"),
        description="Opções adicionais específicas do backend",
    )
    test_charset: str | None = Field(
        default=None,
        alias="DATABASE_TEST_CHARSET",
        validation_alias=AliasChoices("DATABASE_TEST_CHARSET", "DB_TEST_CHARSET"),
        description="Charset para banco de testes",
    )
    test_collation: str | None = Field(
        default=None,
        alias="DATABASE_TEST_COLLATION",
        validation_alias=AliasChoices("DATABASE_TEST_COLLATION", "DB_TEST_COLLATION"),
        description="Collation para banco de testes",
    )
    test_migrate: bool = Field(
        default=True,
        alias="DATABASE_TEST_MIGRATE",
        validation_alias=AliasChoices("DATABASE_TEST_MIGRATE", "DB_TEST_MIGRATE"),
        description="Se deve executar migrações no banco de testes",
    )
    test_mirror: str | None = Field(
        default=None,
        alias="DATABASE_TEST_MIRROR",
        validation_alias=AliasChoices("DATABASE_TEST_MIRROR", "DB_TEST_MIRROR"),
        description="Alias do banco de dados para espelhar em testes",
    )
    test_db_name: str | None = Field(
        default=None,
        alias="DATABASE_TEST_NAME",
        validation_alias=AliasChoices("DATABASE_TEST_NAME", "DB_TEST_NAME"),
        description="Nome do banco de dados de teste",
    )
