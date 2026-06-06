from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinical Trials Query-to-Visualization API"
    # Declared without the CLINICAL_TRIALS_ prefix so LOG_LEVEL works directly.
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "CLINICAL_TRIALS_LOG_LEVEL"))

    model_config = SettingsConfigDict(env_prefix="CLINICAL_TRIALS_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
