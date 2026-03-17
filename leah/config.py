from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str
    leah_model: str = "claude-sonnet-4-6"

    google_credentials_file: Path = Path("credentials/google_credentials.json")
    google_token_file: Path = Path("credentials/google_token.json")

    leah_user_timezone: str = "UTC"
    leah_user_name: str = "there"
    leah_max_memory_messages: int = 100


settings = Settings()
