from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    url: str | None = Field(
        default=None,
        alias="RABBIT_URL",
        description="Complete RabbitMQ URL (e.g., amqp://user:password@host:port/vhost)",
    )
    host: str = Field(
        default="localhost",
        alias="RABBIT_HOST",
        description="RabbitMQ server host",
    )
    port: int = Field(
        default=5672,
        alias="RABBIT_PORT",
        description="RabbitMQ server port",
    )
    vhost: str = Field(
        default="/",
        alias="RABBIT_VHOST",
        description="RabbitMQ virtual host",
    )
    username: str = Field(
        default="guest",
        alias="RABBIT_USERNAME",
        description="RabbitMQ username",
    )
    password: str = Field(
        default="guest",
        alias="RABBIT_PASSWORD",
        description="RabbitMQ password",
    )

    @model_validator(mode="before")
    @classmethod
    def process_url_or_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        data_upper = {k.upper(): v for k, v in values.items()}

        # Se tem URL, extrai os campos individuais
        if data_upper.get("RABBIT_URL"):
            url = data_upper["RABBIT_URL"]
            parsed = urlparse(url)

            if parsed.hostname:
                values["RABBIT_HOST"] = parsed.hostname
            if parsed.port:
                values["RABBIT_PORT"] = parsed.port
            if parsed.username:
                values["RABBIT_USERNAME"] = parsed.username
            if parsed.password:
                values["RABBIT_PASSWORD"] = parsed.password
            if parsed.path and parsed.path.strip("/"):
                values["RABBIT_VHOST"] = parsed.path

        # Se não tem URL mas tem campos individuais, monta a URL
        elif any(
            data_upper.get(key)
            for key in [
                "RABBIT_HOST",
                "RABBIT_PORT",
                "RABBIT_USERNAME",
                "RABBIT_PASSWORD",
                "RABBIT_VHOST",
            ]
        ):
            host = data_upper.get("RABBIT_HOST", "localhost")
            port = data_upper.get("RABBIT_PORT", 5672)
            username = data_upper.get("RABBIT_USERNAME", "guest")
            password = data_upper.get("RABBIT_PASSWORD", "guest")
            vhost = data_upper.get("RABBIT_VHOST", "/")

            values["RABBIT_URL"] = f"amqp://{username}:{password}@{host}:{port}{vhost}"

        return values
