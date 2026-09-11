from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://careeros:change_this_password@postgres:5432/careeros",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    api_cors_origins: str = Field(
        default="http://localhost:3000", alias="API_CORS_ORIGINS"
    )
    
    model_config = SettingsConfigDict(extra="ignore")
    minio_endpoint: str = Field(
        default="minio:9000",
        alias="MINIO_ENDPOINT",
    )

    minio_bucket: str = Field(
        default="careeros-files",
        alias="MINIO_BUCKET",
    )

    minio_root_user: str = Field(
        default="careeros",
        alias="MINIO_ROOT_USER",
    )

    minio_root_password: str = Field(
        default="change_this_password",
        alias="MINIO_ROOT_PASSWORD",
    )

    minio_secure: bool = Field(
        default=False,
        alias="MINIO_SECURE",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
