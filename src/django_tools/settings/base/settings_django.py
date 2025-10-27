from contextlib import suppress
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .infra import DatabaseSettings


class DjangoSettingsBaseModel(BaseSettings):
    """Django settings with DJANGO_ prefix."""

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        serialize_by_alias=True,
    )

    secret_key: str = Field(
        default="django-insecure-change-me-in-production",
        alias="SECRET_KEY",
        validation_alias=AliasChoices("SECRET_KEY", "DJANGO_SECRET_KEY"),
        description="Django secret key",
    )
    debug: bool = Field(
        default=True,
        alias="DEBUG",
        validation_alias=AliasChoices("DEBUG", "DJANGO_DEBUG"),
        description="Debug mode",
    )
    allowed_hosts: list[str] = Field(
        default=["*"],
        alias="ALLOWED_HOSTS",
        validation_alias=AliasChoices("ALLOWED_HOSTS", "DJANGO_ALLOWED_HOSTS"),
        description="Allowed hosts",
    )
    root_urlconf: str = Field(
        default="core.urls",
        alias="ROOT_URLCONF",
        validation_alias=AliasChoices("ROOT_URLCONF", "DJANGO_ROOT_URLCONF"),
        description="Root URL configuration",
    )

    # ==================================================================================
    # INTERNATIONALIZATION SETTINGS
    # ==================================================================================
    language_code: str = Field(
        default="pt-br",
        alias="LANGUAGE_CODE",
        validation_alias=AliasChoices("LANGUAGE_CODE", "DJANGO_LANGUAGE_CODE"),
        description="Language code",
    )
    time_zone: str = Field(
        default="UTC",
        alias="TIME_ZONE",
        validation_alias=AliasChoices("TIME_ZONE", "DJANGO_TIME_ZONE"),
        description="Timezone",
    )
    use_i18n: bool = Field(
        default=True,
        alias="USE_I18N",
        validation_alias=AliasChoices("USE_I18N", "DJANGO_USE_I18N"),
        description="Use internationalization",
    )
    use_tz: bool = Field(
        default=True,
        alias="USE_TZ",
        validation_alias=AliasChoices("USE_TZ", "DJANGO_USE_TZ"),
        description="Use timezone aware",
    )

    # ==================================================================================
    # TEMPLATE SETTINGS
    # ==================================================================================
    template_backend: str = Field(
        default="django.template.backends.django.DjangoTemplates",
        alias="TEMPLATE_BACKEND",
        validation_alias=AliasChoices("TEMPLATE_BACKEND", "DJANGO_TEMPLATE_BACKEND"),
        description="Template backend",
    )
    template_dirs: list[str] = Field(
        default_factory=list,
        alias="TEMPLATE_DIRS",
        validation_alias=AliasChoices("TEMPLATE_DIRS", "DJANGO_TEMPLATE_DIRS"),
        description="Template directories",
    )
    template_app_dirs: bool = Field(
        default=True,
        alias="TEMPLATE_APP_DIRS",
        validation_alias=AliasChoices("TEMPLATE_APP_DIRS", "DJANGO_TEMPLATE_APP_DIRS"),
        description="Search for templates in apps",
    )

    # ==================================================================================
    # APPLICATION SETTINGS
    # ==================================================================================
    api_name: str = Field(
        default="core",
        alias="API_NAME",
        validation_alias=AliasChoices("API_NAME", "DJANGO_API_NAME"),
        description="API name",
    )
    default_auto_field: str = Field(
        default="django.db.models.BigAutoField",
        alias="DEFAULT_AUTO_FIELD",
        validation_alias=AliasChoices("DEFAULT_AUTO_FIELD", "DJANGO_DEFAULT_AUTO_FIELD"),
        description="Default auto increment field",
    )

    # ==================================================================================
    # FIELD VALIDATORS
    # ==================================================================================
    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: Any) -> list[str]:
        """Parse ALLOWED_HOSTS from string to list."""
        import json

        if not value or str(value).strip() == "":
            return ["*"]

        # Se já é uma lista, retorna como está
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]

        text = str(value).strip()

        # Try first to interpret as JSON array
        if text.startswith("[") and text.endswith("]"):
            with suppress(Exception):
                data = json.loads(text)
                if isinstance(data, list):
                    return [str(x).strip() for x in data if str(x).strip()]

        # Fallback to CSV parsing
        hosts = [h.strip() for h in text.split(",") if h.strip()]
        return hosts or ["*"]


class DjangoSettings(DjangoSettingsBaseModel):
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
