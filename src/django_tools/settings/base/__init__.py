from typing import Any

from .infra.settings_celery import CelerySettings
from .infra.settings_database import DatabaseSettings
from .infra.settings_rabbit import RabbitMQSettings
from .infra.settings_redis import RedisSettings
from .settings_django import DjangoSettingsBaseModel


class Settings:
    def __init__(self, env_file: str = ".env"):
        self.dj = DjangoSettingsBaseModel(_env_file=env_file)
        self.celery = CelerySettings(_env_file=env_file)
        self.db = DatabaseSettings(_env_file=env_file)
        self.rabbit = RabbitMQSettings(_env_file=env_file)
        self.redis = RedisSettings(_env_file=env_file)

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        return {
            **self.dj.model_dump(by_alias=kwargs.pop("by_alias", True), *args, **kwargs),
            **self.celery.model_dump(by_alias=kwargs.pop("by_alias", True), *args, **kwargs),
            **self.db.model_dump(by_alias=kwargs.pop("by_alias", True), *args, **kwargs),
            **self.rabbit.model_dump(by_alias=kwargs.pop("by_alias", True), *args, **kwargs),
            **self.redis.model_dump(by_alias=kwargs.pop("by_alias", True), *args, **kwargs),
        }

    def __str__(self) -> str:
        parts = [
            f"DJANGO SETTINGS:\n{self.dj}\n",
            f"CELERY SETTINGS:\n{self.celery}\n",
            f"DATABASE SETTINGS:\n{self.db}\n",
            f"RABBITMQ SETTINGS:\n{self.rabbit}\n",
            f"REDIS SETTINGS:\n{self.redis}\n",
        ]
        return "\n".join(parts)


if __name__ == "__main__":
    settings = Settings()
    print(settings)
