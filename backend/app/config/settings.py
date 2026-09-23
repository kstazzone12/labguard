import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("LABGUARD_APP_NAME", "LABGUARD")
    app_version: str = os.getenv("LABGUARD_APP_VERSION", "0.1.0")
    environment: str = os.getenv("LABGUARD_ENVIRONMENT", "development")
    database_url: str = os.getenv(
        "LABGUARD_DATABASE_URL", "sqlite:///./labguard.db"
    )
    synthetic_data_only: bool = _env_bool("LABGUARD_SYNTHETIC_DATA_ONLY", False)


settings = Settings()
