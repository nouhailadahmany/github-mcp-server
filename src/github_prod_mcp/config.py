from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str = Field(..., alias="GITHUB_TOKEN")
    github_api_base_url: str = Field(
        default="https://api.github.com",
        alias="GITHUB_API_BASE_URL",
    )
    github_api_version: str = Field(
        default="2022-11-28",
        alias="GITHUB_API_VERSION",
    )
    github_user_agent: str = Field(
        default="github-prod-mcp/0.1.0",
        alias="GITHUB_USER_AGENT",
    )
    github_timeout_seconds: float = Field(
        default=30.0,
        alias="GITHUB_TIMEOUT_SECONDS",
    )
    rest_host: str = Field(default="0.0.0.0", alias="REST_HOST")
    rest_port: int = Field(default=8080, alias="REST_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.model_validate({})
    