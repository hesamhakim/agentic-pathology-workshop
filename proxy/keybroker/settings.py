from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KEYBROKER_",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = "https://api.openai.com"

    tokens_file: Path = Path("/etc/keybroker/tokens.json")

    daily_usd_limit: float = 5.00
    tpm_limit: int = 30_000

    state_db: Path = Path("/var/lib/keybroker/state.db")

    log_prompts: bool = True
    log_dir: Path = Path("/var/log/keybroker")

    request_timeout_s: float = 60.0


def get_settings() -> Settings:
    return Settings()
