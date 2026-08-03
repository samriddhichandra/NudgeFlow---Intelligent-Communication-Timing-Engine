from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql+psycopg2://ict_user:ict_password@db:5432/ict_engine"
    app_env: str = "development"


settings = Settings()
