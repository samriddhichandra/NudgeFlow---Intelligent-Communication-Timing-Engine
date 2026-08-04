import os
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings, SettingsConfigDict


# Vercel does not run this repository's Docker Compose PostgreSQL service.
# When no managed DATABASE_URL is configured, use its writable temporary
# directory so the demo can still accept requests. This data is ephemeral.
# `gettempdir()` resolves to `/tmp` in the Vercel Linux runtime and to the
# appropriate writable temp directory on other platforms.
TEMPORARY_VERCEL_DATABASE_PATH = Path(gettempdir()) / "nudgeflow.db"
TEMPORARY_VERCEL_DATABASE_URL = (
    f"sqlite:///{TEMPORARY_VERCEL_DATABASE_PATH.as_posix()}"
)
DEFAULT_DATABASE_URL = (
    TEMPORARY_VERCEL_DATABASE_URL
    if os.getenv("VERCEL")
    else "postgresql+psycopg2://ict_user:ict_password@db:5432/ict_engine"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = DEFAULT_DATABASE_URL
    app_env: str = "development"

    @property
    def uses_temporary_vercel_database(self) -> bool:
        return self.database_url == TEMPORARY_VERCEL_DATABASE_URL


settings = Settings()
