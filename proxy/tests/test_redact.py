from keybroker.redact import redact_payload, redact_text


def test_redact_text_strips_openai_keys():
    out = redact_text("here is a key sk-AbCdEfGhIjKlMnOpQrStUvWxYz12 and more text")
    assert "sk-AbCdEfGhIjKlMnOpQrStUvWxYz12" not in out
    assert "[REDACTED]" in out


def test_redact_text_strips_ssn_pattern():
    out = redact_text("patient SSN 123-45-6789 confidential")
    assert "123-45-6789" not in out
    assert "[REDACTED]" in out


def test_redact_text_strips_credit_card_pattern():
    out = redact_text("card 4111111111111111 stored")
    assert "4111111111111111" not in out


def test_redact_payload_redacts_string_content():
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "my key is sk-1234567890abcdefghijklm"},
        ],
    }
    out = redact_payload(payload)
    assert "[REDACTED]" in out["messages"][0]["content"]
    assert payload["messages"][0]["content"] != out["messages"][0]["content"]


def test_redact_payload_handles_multimodal_content():
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "see SSN 999-99-9999"},
                    {"type": "image_url", "image_url": {"url": "data:..."}},
                ],
            }
        ],
    }
    out = redact_payload(payload)
    text_part = out["messages"][0]["content"][0]
    assert "[REDACTED]" in text_part["text"]
    image_part = out["messages"][0]["content"][1]
    assert image_part["type"] == "image_url"


def test_redact_payload_no_messages_passthrough():
    payload = {"model": "gpt-4o", "input": "embedding text"}
    assert redact_payload(payload) == payload
