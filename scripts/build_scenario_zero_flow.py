#!/usr/bin/env python3
"""Build the 0_general_chatbot flow programmatically.

A deliberately generic chatbot — the warm-up baseline for the workshop's
pedagogical contrast. Layout:

  File1 (optional) ─┐
  File2 (optional) ─┤
  File3 (optional) ─┼─→ GeneralChatbot ──→ ChatOutput
  File4 (optional) ─┤
  ChatInput ────────┘

The chatbot has no domain specialization. Attendees upload whatever
files they want, type whatever question they want, and get one
LLM-generated answer back. The suggested workshop exercise — upload
Omar's four AML PDFs and ask for an integrated diagnostic report —
then sets up the side-by-side comparison with Scenario D's
seven-component agentic workflow on the same input.

Mirrors scripts/build_scenario_d_v2_flow.py — same edge encoding,
upload-and-save pattern.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

import httpx


LF_QUOTE = "œ"


def encode_handle(d: dict) -> str:
    return json.dumps(d, separators=(",", ":")).replace('"', LF_QUOTE)


def login(client: httpx.Client) -> str:
    import os
    user = os.environ.get("WORKSHOP_LF_USER", "langflow")
    pw = os.environ.get("WORKSHOP_LF_PASSWORD", "langflow")
    resp = client.post(
        "/api/v1/login",
        data={"username": user, "password": pw},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_all_components(client: httpx.Client) -> dict:
    resp = client.get("/api/v1/all")
    resp.raise_for_status()
    return resp.json()


def get_component(all_components: dict, category: str, name: str) -> dict:
    if category not in all_components:
        raise SystemExit(f"category {category!r} not in registry. Sample: {sorted(all_components)[:10]}")
    if name not in all_components[category]:
        raise SystemExit(f"component {name!r} not in {category!r}. Available: {sorted(all_components[category])}")
    return all_components[category][name]


def make_node(template: dict, component_name: str, position: tuple[float, float]) -> dict:
    node_id = f"{component_name.replace(' ', '_')}-{secrets.token_hex(3)}"
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": position[0], "y": position[1]},
        "data": {
            "id": node_id,
            "type": component_name,
            "node": template,
            "showNode": True,
        },
    }


def make_edge(
    source_node: dict,
    source_output_name: str,
    source_output_types: list[str],
    target_node: dict,
    target_field: str,
    target_input_types: list[str],
) -> dict:
    src_id = source_node["id"]
    tgt_id = target_node["id"]
    src_data_type = source_node["data"]["type"]

    source_handle_dict = {
        "dataType": src_data_type,
        "id": src_id,
        "name": source_output_name,
        "output_types": source_output_types,
    }
    target_handle_dict = {
        "fieldName": target_field,
        "id": tgt_id,
        "inputTypes": target_input_types,
        "type": "other",
    }
    src_handle = encode_handle(source_handle_dict)
    tgt_handle = encode_handle(target_handle_dict)
    return {
        "source": src_id,
        "sourceHandle": src_handle,
        "target": tgt_id,
        "targetHandle": tgt_handle,
        "data": {
            "sourceHandle": source_handle_dict,
            "targetHandle": target_handle_dict,
        },
        "id": f"xy-edge__{src_id}{src_handle}-{tgt_id}{tgt_handle}",
        "animated": False,
        "className": "",
        "selected": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:7860")
    parser.add_argument("--name", default="0_general_chatbot")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    out_path = Path(__file__).resolve().parents[1] / "langflow_flows" / "0_general_chatbot.json"

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        cat_zero = "api_scenario_zero"
        cat_io = "input_output"
        cat_files = "files_and_knowledge"

        chat_in = get_component(all_components, cat_io, "ChatInput")
        file_tpl = get_component(all_components, cat_files, "File")
        chatbot = get_component(all_components, cat_zero, "GeneralChatbot")
        chat_out = get_component(all_components, cat_io, "ChatOutput")

        # Four file nodes stacked vertically on the left, chat input below,
        # one chatbot in the middle, chat output on the right.
        n_chatin = make_node(chat_in,    "ChatInput",   (50, 950))
        n_file1  = make_node(file_tpl,   "File",        (50, 100))
        n_file2  = make_node(file_tpl,   "File",        (50, 320))
        n_file3  = make_node(file_tpl,   "File",        (50, 540))
        n_file4  = make_node(file_tpl,   "File",        (50, 760))
        n_chatbot = make_node(chatbot,   "GeneralChatbot",         (700, 500))
        n_chatout = make_node(chat_out,  "ChatOutput",  (1300, 500))

        nodes = [n_file1, n_file2, n_file3, n_file4, n_chatin, n_chatbot, n_chatout]

        edges = [
            # 4× File -> NaiveChatbot.fileN (Message)
            make_edge(n_file1, "message", ["Message"], n_chatbot, "file1", ["Message"]),
            make_edge(n_file2, "message", ["Message"], n_chatbot, "file2", ["Message"]),
            make_edge(n_file3, "message", ["Message"], n_chatbot, "file3", ["Message"]),
            make_edge(n_file4, "message", ["Message"], n_chatbot, "file4", ["Message"]),
            # ChatInput -> NaiveChatbot.user_message (Message)
            make_edge(n_chatin, "message", ["Message"], n_chatbot, "user_message", ["Message"]),
            # NaiveChatbot -> ChatOutput (Message)
            make_edge(n_chatbot, "reply", ["Message"], n_chatout, "input_value", ["Message"]),
        ]

        flow_payload = {
            "name": args.name,
            "description": (
                "General chatbot — a generic single-LLM-call assistant that "
                "accepts up to four file attachments and a chat message. The "
                "workshop's warm-up exercise: upload the four Omar AML PDFs, "
                "ask in Playground for an integrated diagnostic report, then "
                "compare what this chatbot produces against the seven-"
                "component agentic workflow in Scenario D running on the "
                "same input. The chatbot itself has no specialization — "
                "everything happens in one prompt."
            ),
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.5},
            },
        }

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(flow_payload, indent=2) + "\n")
        print(f"=> saved {out_path.relative_to(Path.cwd())} ({out_path.stat().st_size:,} bytes)")

        if args.no_upload:
            print("=> --no-upload set; skipping POST")
            return 0

        existing = client.get("/api/v1/flows/", params={"page": 1, "size": 100}).json()
        if isinstance(existing, dict):
            existing = existing.get("items", existing.get("flows", []))
        for f in existing:
            if f.get("name") == args.name:
                client.delete(f"/api/v1/flows/{f['id']}")
                print(f"=> deleted previous {args.name} (id={f['id'][:8]})")

        print("=> upload to LangFlow")
        resp = client.post("/api/v1/flows/", json=flow_payload)
        if resp.status_code >= 400:
            print(f"   upload failed: {resp.status_code}")
            print(resp.text[:1500])
            return 1
        flow_id = resp.json()["id"]
        print(f"   flow_id = {flow_id}")
        print(f"   open in UI: {args.host}/flow/{flow_id}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
