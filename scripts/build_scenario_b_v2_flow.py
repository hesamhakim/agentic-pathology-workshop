#!/usr/bin/env python3
"""Build the B_longitudinal_ghost flow programmatically.

Mirrors scripts/build_scenario_{a,c}_v2_flow.py.

Wiring:
  ChatInput -> PipelineConfig --(run_config)--> TemporalSynthesizer
                              \\--(run_config)--> SDoHExtractor (parallel)
  TemporalSynthesizer -> Detective --(timeline)
  RequestParser ------> Detective --(claims, parallel branch)
  Detective -> QAReviewer -> ReportFormatter
  SDoHExtractor ------> ReportFormatter (parallel, joins late)
  ReportFormatter -> ChatOutput
"""

from __future__ import annotations

import argparse
import json
import secrets
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
        raise SystemExit(f"category {category!r} not in registry.")
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
        "data": {"sourceHandle": source_handle_dict, "targetHandle": target_handle_dict},
        "id": f"xy-edge__{src_id}{src_handle}-{tgt_id}{tgt_handle}",
        "animated": False,
        "className": "",
        "selected": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:7860")
    parser.add_argument("--name", default="B_longitudinal_ghost")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    out_path = Path(__file__).resolve().parents[1] / "langflow_flows" / "B_longitudinal_ghost.json"

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        cat_b = "api_scenario_b"
        cat_io = "input_output"

        chat_in = get_component(all_components, cat_io, "ChatInput")
        cfg = get_component(all_components, cat_b, "PipelineConfig S-B.V2")
        synth = get_component(all_components, cat_b, "TemporalSynthesizer S-B.V2")
        req_parser = get_component(all_components, cat_b, "RequestParser S-B.V2")
        detective = get_component(all_components, cat_b, "Detective S-B.V2")
        sdoh = get_component(all_components, cat_b, "SDoHExtractor S-B.V2")
        qa = get_component(all_components, cat_b, "QAReviewer S-B.V2")
        report = get_component(all_components, cat_b, "ReportFormatter S-B.V2")
        chat_out = get_component(all_components, cat_io, "ChatOutput")

        n_chatin = make_node(chat_in, "ChatInput", (50, 250))
        n_cfg = make_node(cfg, "PipelineConfig S-B.V2", (450, 250))
        n_synth = make_node(synth, "TemporalSynthesizer S-B.V2", (900, 50))
        n_req = make_node(req_parser, "RequestParser S-B.V2", (900, 600))
        n_sdoh = make_node(sdoh, "SDoHExtractor S-B.V2", (900, 1100))
        n_detective = make_node(detective, "Detective S-B.V2", (1350, 300))
        n_qa = make_node(qa, "QAReviewer S-B.V2", (1800, 300))
        n_report = make_node(report, "ReportFormatter S-B.V2", (2250, 700))
        n_chatout = make_node(chat_out, "ChatOutput", (2700, 700))

        nodes = [n_chatin, n_cfg, n_synth, n_req, n_sdoh, n_detective, n_qa, n_report, n_chatout]

        edges = [
            # ChatInput -> PipelineConfig (Message)
            make_edge(n_chatin, "message", ["Message"], n_cfg, "user_message", ["Message"]),
            # PipelineConfig -> TemporalSynthesizer (Data, run_config)
            make_edge(n_cfg, "run_config", ["Data"], n_synth, "run_config", ["Data"]),
            # PipelineConfig -> SDoHExtractor (Data, run_config) — same source, second target
            make_edge(n_cfg, "run_config", ["Data"], n_sdoh, "run_config", ["Data"]),
            # TemporalSynthesizer -> Detective.timeline (Data)
            make_edge(n_synth, "timeline", ["Data"], n_detective, "timeline", ["Data"]),
            # RequestParser -> Detective.claims (Message, parallel branch)
            make_edge(n_req, "claims", ["Message"], n_detective, "claims", ["Message"]),
            # Detective -> QAReviewer (Data)
            make_edge(n_detective, "findings", ["Data"], n_qa, "findings_input", ["Data"]),
            # QAReviewer -> ReportFormatter.reviewed (Data)
            make_edge(n_qa, "reviewed", ["Data"], n_report, "reviewed", ["Data"]),
            # SDoHExtractor -> ReportFormatter.sdoh (Data, parallel branch joins at the end)
            make_edge(n_sdoh, "sdoh", ["Data"], n_report, "sdoh", ["Data"]),
            # ReportFormatter -> ChatOutput (Message)
            make_edge(n_report, "report", ["Message"], n_chatout, "input_value", ["Message"]),
        ]

        flow_payload = {
            "name": args.name,
            "description": "Scenario B v2: longitudinal-record reconciliation. Detective compares chart timeline vs current request claims; SDoH agent runs in parallel.",
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.45},
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
    raise SystemExit(main())
