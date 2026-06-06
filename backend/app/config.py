from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinical Trials Query-to-Visualization API"
    default_data_mode: Literal["cache", "live"] = "cache"

    model_config = SettingsConfigDict(env_prefix="CLINICAL_TRIALS_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
