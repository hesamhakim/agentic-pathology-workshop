#!/usr/bin/env python3
"""Build, save, and run the 00_smoke flow purely through LangFlow's REST API.

Use this when LangFlow's UI is uncooperative or you want a code-driven smoke.
The flow wired here is:

    Chat Input -> KeyBroker LLM -> Chat Output

The KeyBroker LLM component is our custom one at
langflow_flows/components/workshop/keybroker_llm.py.

Usage:
    python scripts/run_smoke_via_api.py [--host http://localhost:7860]
                                        [--prompt "Reply with exactly: PONG"]
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from typing import Any

import httpx


def login(client: httpx.Client) -> str:
    resp = client.post(
        "/api/v1/login",
        data={"username": "langflow", "password": "langflow"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    return token


def create_api_key(client: httpx.Client, name: str = "smoke-script") -> str:
    """LangFlow >=1.5 requires an api key (not just JWT) on /run. Mint one."""
    resp = client.post("/api/v1/api_key/", json={"name": name})
    resp.raise_for_status()
    return resp.json()["api_key"]


def get_component_template(client: httpx.Client, category: str, name: str) -> dict[str, Any]:
    resp = client.get("/api/v1/all")
    resp.raise_for_status()
    data = resp.json()
    if category not in data or name not in data[category]:
        raise SystemExit(f"Component {category}/{name} not registered. Available: {list(data.keys())[:5]}...")
    return data[category][name]


def make_node(node_id: str, name: str, template: dict[str, Any], x: float, y: float) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "id": node_id,
            "type": name,
            "node": template,
        },
    }


def make_edge(src: str, src_handle: str, tgt: str, tgt_handle: str) -> dict[str, Any]:
    return {
        "id": f"edge-{src}-{tgt}",
        "source": src,
        "target": tgt,
        "sourceHandle": src_handle,
        "targetHandle": tgt_handle,
        "type": "default",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:7860")
    parser.add_argument("--prompt", default="Reply with exactly: PONG")
    parser.add_argument("--flow-name", default="00_smoke")
    args = parser.parse_args()

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print(f"=> login as default langflow user")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> mint an API key (required by /run since LangFlow 1.5)")
        api_key = create_api_key(client, name=f"smoke-{uuid.uuid4().hex[:6]}")

        print("=> fetch component templates")
        chat_in = get_component_template(client, "input_output", "ChatInput")
        chat_out = get_component_template(client, "input_output", "ChatOutput")
        kb_llm = get_component_template(client, "workshop", "KeyBrokerLLM")
        print(f"   ChatInput template OK ({len(chat_in.get('template', {}))} fields)")
        print(f"   ChatOutput template OK ({len(chat_out.get('template', {}))} fields)")
        print(f"   KeyBrokerLLM template OK ({len(kb_llm.get('template', {}))} fields)")

        in_id = f"ChatInput-{uuid.uuid4().hex[:5]}"
        llm_id = f"KeyBrokerLLM-{uuid.uuid4().hex[:5]}"
        out_id = f"ChatOutput-{uuid.uuid4().hex[:5]}"

        flow_data = {
            "nodes": [
                make_node(in_id, "ChatInput", chat_in, 100, 200),
                make_node(llm_id, "KeyBrokerLLM", kb_llm, 500, 200),
                make_node(out_id, "ChatOutput", chat_out, 900, 200),
            ],
            "edges": [
                make_edge(in_id, "message", llm_id, "input_value"),
                make_edge(llm_id, "message", out_id, "input_value"),
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
        }

        print(f"=> create flow '{args.flow_name}'")
        resp = client.post(
            "/api/v1/flows/",
            json={
                "name": args.flow_name,
                "description": "API-driven smoke test for KeyBroker -> OpenRouter -> Phoenix",
                "data": flow_data,
            },
        )
        if resp.status_code >= 400:
            print(f"   create failed: {resp.status_code}")
            print(resp.text[:1500])
            return 1
        flow = resp.json()
        flow_id = flow["id"]
        print(f"   flow_id = {flow_id}")

        print(f"=> run flow with prompt: {args.prompt!r}")
        resp = client.post(
            f"/api/v1/run/{flow_id}",
            json={
                "input_value": args.prompt,
                "input_type": "chat",
                "output_type": "chat",
            },
            headers={"x-api-key": api_key},
        )
        if resp.status_code >= 400:
            print(f"   run failed: {resp.status_code}")
            print(resp.text[:2000])
            return 1
        result = resp.json()

        print()
        print("=> response payload (truncated):")
        text = json.dumps(result, indent=2)
        print(text[:2000])
        if len(text) > 2000:
            print(f"... ({len(text) - 2000} more bytes)")

        # Best-effort: extract the final message text
        try:
            msg = result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            print()
            print(f"=> assistant said: {msg!r}")
        except (KeyError, IndexError, TypeError):
            pass

        print()
        print(f"=> open Phoenix at http://localhost:6006 to see the trace")
        return 0


if __name__ == "__main__":
    sys.exit(main())
