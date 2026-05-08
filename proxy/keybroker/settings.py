from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KEYBROKER_",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    # Single upstream key (legacy / dev). For multi-key fan-out (workshop scale)
    # set OPENAI_API_KEYS (semicolon-separated) instead — it takes precedence.
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_api_keys: str = Field(default="", alias="OPENAI_API_KEYS")
    openai_base_url: str = "https://api.openai.com"

    tokens_file: Path = Path("/etc/keybroker/tokens.json")

    # Per-attendee caps (defense against runaway loops on a single user)
    daily_usd_limit: float = 5.00
    tpm_limit: int = 30_000

    # Global pool cap (defense for the workshop's whole budget). Sum of ALL
    # attendees' spend can never exceed this on a single UTC day. 0 = disabled.
    global_daily_usd_limit: float = 0.0

    # Hard ceiling on max_tokens per request — clamps over-aggressive prompts.
    max_output_tokens_ceiling: int = 3000

    state_db: Path = Path("/var/lib/keybroker/state.db")

    log_prompts: bool = True
    log_dir: Path = Path("/var/log/keybroker")

    request_timeout_s: float = 60.0

    @property
    def upstream_keys(self) -> list[str]:
        """Resolved list of upstream keys, in order. Empty if neither var is set."""
        if self.openai_api_keys.strip():
            return [k.strip() for k in self.openai_api_keys.split(";") if k.strip()]
        if self.openai_api_key.strip():
            return [self.openai_api_key.strip()]
        return []


def get_settings() -> Settings:
    return Settings()
