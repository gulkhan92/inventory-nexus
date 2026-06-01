from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# base class
class Settings(BaseSettings):
    app_name: str = "Inventory Nexus"
    environment: Literal["local", "test", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="sqlite:///./inventory_nexus.db",
        description="Use postgresql+psycopg://user:password@host:5432/dbname in production.",
    )
    secret_key: str = "change-me-before-production"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    seed_csv_path: str = (
        "../Multi source Customer Mart for Female Recommendati/MultiSource_Female_CustMart.csv"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
