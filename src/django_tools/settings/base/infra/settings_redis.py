from __future__ import annotations

import contextlib
from typing import Any
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    url: str | None = Field(
        default=None,
        alias="REDIS_URL",
        description="Complete Redis URL (e.g., redis://:password@host:port/db)",
    )
    host: str = Field(
        default="localhost",
        alias="REDIS_HOST",
        description="Redis server host",
    )
    port: int = Field(
        default=6379,
        alias="REDIS_PORT",
        description="Redis server port",
    )
    db: int = Field(
        default=0,
        alias="REDIS_DB",
        description="Redis database number",
    )
    password: str | None = Field(
        default=None,
        alias="REDIS_PASSWORD",
        description="Redis password (optional)",
    )

    @model_validator(mode="before")
    @classmethod
    def process_url_or_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        data_upper = {k.upper(): v for k, v in values.items()}

        # Se tem URL, extrai os campos individuais
        if data_upper.get("REDIS_URL"):
            url = data_upper["REDIS_URL"]
            parsed = urlparse(url)

            if parsed.hostname:
                values["REDIS_HOST"] = parsed.hostname
            if parsed.port:
                values["REDIS_PORT"] = parsed.port
            if parsed.password:
                values["REDIS_PASSWORD"] = parsed.password
            if parsed.path and parsed.path.strip("/"):
                with contextlib.suppress(ValueError):
                    values["REDIS_DB"] = int(parsed.path.strip("/"))

        # Se não tem URL mas tem campos individuais, monta a URL
        elif any(data_upper.get(key) for key in ["REDIS_HOST", "REDIS_PORT", "REDIS_DB", "REDIS_PASSWORD"]):
            host = data_upper.get("REDIS_HOST", "localhost")
            port = data_upper.get("REDIS_PORT", 6379)
            db = data_upper.get("REDIS_DB", 0)
            password = data_upper.get("REDIS_PASSWORD")

            password_part = f":{password}" if password else ""
            values["REDIS_URL"] = f"redis://{password_part}@{host}:{port}/{db}"

        return values
