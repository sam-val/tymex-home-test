import os
from enum import Enum
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModeEnum(str, Enum):
    testing = "testing"  # for pytest
    local = "local"
    dev = "dev"
    uat = "uat"
    prod = "prod"


class Settings(BaseSettings):
    """
    Application settings pulled from environment variables or a .env file.
    You can extend this with your own config (e.g. SMTP, 3rd party APIs, etc.).
    """

    APP_NAME: str = "tymex"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = Field(default_factory=list)
    MODE: ModeEnum = ModeEnum.dev

    # database
    ASYNC_SQLITE_URI: Optional[str] = "sqlite+aiosqlite:///./test.db"
    ASYNC_UNITEST_SQLITE_URI: Optional[str] = "sqlite+aiosqlite:///./unittest.db"
    # parts of async DB URI
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    # test db
    TEST_DATABASE_USER: Optional[str] = None
    TEST_DATABASE_PASSWORD: Optional[str] = None
    TEST_DATABASE_HOST: Optional[str] = None
    TEST_DATABASE_PORT: Optional[int] = None
    TEST_DATABASE_NAME: Optional[str] = None

    DATABASE_URI: PostgresDsn | str = ""
    ASYNC_DATABASE_URI: PostgresDsn | str = ""

    # redis
    REDIS_URI: Optional[str] = None

    # Add more custom settings as needed
    # e.g. rate_limit_per_minute: int = 30

    @field_validator("DATABASE_URI", mode="after")
    def assemble_sync_db(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme="postgresql",
                    username=info.data["DATABASE_USER"],
                    password=info.data["DATABASE_PASSWORD"],
                    host=info.data["DATABASE_HOST"],
                    port=info.data["DATABASE_PORT"],
                    path=info.data["DATABASE_NAME"],
                )
        return v

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_async_db(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            if v == "":
                mode = info.data.get("MODE")
                print("mode: ", mode)
                print(info.data)
                if mode == ModeEnum.testing:
                    return PostgresDsn.build(
                        scheme="postgresql+asyncpg",
                        username=info.data["TEST_DATABASE_USER"],
                        password=info.data["TEST_DATABASE_PASSWORD"],
                        host=info.data["TEST_DATABASE_HOST"],
                        port=info.data["TEST_DATABASE_PORT"],
                        path=info.data["TEST_DATABASE_NAME"],
                    )

                return PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DATABASE_USER"],
                    password=info.data["DATABASE_PASSWORD"],
                    host=info.data["DATABASE_HOST"],
                    port=info.data["DATABASE_PORT"],
                    path=info.data["DATABASE_NAME"],
                )
        return v

    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        extra="allow",
    )


def load_settings_from_vault() -> Settings:
    """
    Placeholder for loading secrets from a secret manager like HashiCorp Vault.
    Replace with your logic if you decide to move away from .env files.
    """
    raise NotImplementedError("Vault integration is not implemented.")


# lru cache for singleton pattern
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns application settings. Chooses between environment file and Vault.
    Set `USE_VAULT=true` in your environment to switch to vault loader.
    """
    if os.getenv("USE_VAULT", "false").lower() == "true":
        return load_settings_from_vault()
    return Settings()
