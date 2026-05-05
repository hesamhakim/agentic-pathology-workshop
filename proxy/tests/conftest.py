import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from keybroker.main import create_app
from keybroker.settings import Settings


@pytest.fixture
def tokens_file(tmp_path: Path) -> Path:
    p = tmp_path / "tokens.json"
    p.write_text(
        json.dumps(
            {
                "tok_alice": {
                    "attendee_id": "alice@example.org",
                    "daily_usd_cap": 5.0,
                    "tpm_limit": 30000,
                },
                "tok_bob_low": {
                    "attendee_id": "bob@example.org",
                    "daily_usd_cap": 0.001,
                    "tpm_limit": 30000,
                },
            }
        )
    )
    return p


@pytest.fixture
def settings(tmp_path: Path, tokens_file: Path) -> Settings:
    return Settings(
        openai_api_key="sk-test-real-key",
        openai_base_url="http://upstream.test",
        tokens_file=tokens_file,
        daily_usd_limit=5.0,
        tpm_limit=30000,
        state_db=tmp_path / "state.db",
        log_dir=tmp_path / "logs",
        log_prompts=False,
    )


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
