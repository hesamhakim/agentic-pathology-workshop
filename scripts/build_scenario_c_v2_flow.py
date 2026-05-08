#!/usr/bin/env python3
"""Build the C_digital_thread_v2 flow programmatically.

Wires the six v2 components plus a Chat Output, with the right input/output
types so LangFlow's graph builder is happy:

  TriageAgent (Data) ──▶ EligibilityFilter (Data)
                           ──▶ RoutingAgent (Data) ──▶ QAReviewer (Data)
                                  ▲                         ──▶ ReportFormatter (Data)
                                  │                                    ──▶ Chat Output
  CapacityAdvisor (Message) ──────┘

CapacityAdvisor is independent — it loads instruments.csv directly and feeds
its narrative into RoutingAgent only.

Saves the flow JSON to langflow_flows/C_digital_thread_v2.json AND
imports it into the running LangFlow instance via API.

Usage:
    python scripts/build_scenario_c_v2_flow.py [--host http://localhost:7860]
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

import httpx


# LangFlow uses the OE-ligature character ('œ', U+0153) as a stand-in for
# double quotes inside its handle-id strings, so quoted JSON can be embedded
# without escape headaches.
LF_QUOTE = "œ"


def encode_handle(d: dict) -> str:
    """Encode a handle dict using LangFlow's `œ`-substitution convention."""
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
        raise SystemExit(f"category {category!r} not in registry. Available: {sorted(all_components)[:10]}")
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
    target_type: str = "other",
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
        "type": target_type,
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
    parser.add_argument("--name", default="C_digital_thread_v2")
    parser.add_argument("--no-upload", action="store_true", help="Save JSON to disk only, don't POST to LangFlow.")
    args = parser.parse_args()

    out_path = Path(__file__).resolve().parents[1] / "langflow_flows" / "C_digital_thread_v2.json"

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        # Fetch templates by name
        cat_c = "api_scenario_c"
        cat_io = "input_output"
        chat_in = get_component(all_components, cat_io, "ChatInput")
        cfg = get_component(all_components, cat_c, "PipelineConfig S-C.V2")
        triage = get_component(all_components, cat_c, "TriageAgent S-C.V2")
        capacity = get_component(all_components, cat_c, "CapacityAdvisor S-C.V2")
        eligibility = get_component(all_components, cat_c, "EligibilityFilter S-C.V2")
        routing = get_component(all_components, cat_c, "RoutingAgent S-C.V2")
        qa = get_component(all_components, cat_c, "QAReviewer S-C.V2")
        report = get_component(all_components, cat_c, "ReportFormatter S-C.V2")
        chat_out = get_component(all_components, cat_io, "ChatOutput")

        # Layout (x, y) — left to right with vertical offsets
        n_chatin = make_node(chat_in, "ChatInput", (50, 250))
        n_cfg = make_node(cfg, "PipelineConfig S-C.V2", (450, 250))
        n_triage = make_node(triage, "TriageAgent S-C.V2", (900, 100))
        n_capacity = make_node(capacity, "CapacityAdvisor S-C.V2", (900, 600))
        n_eligibility = make_node(eligibility, "EligibilityFilter S-C.V2", (1350, 100))
        n_routing = make_node(routing, "RoutingAgent S-C.V2", (1800, 350))
        n_qa = make_node(qa, "QAReviewer S-C.V2", (2250, 350))
        n_report = make_node(report, "ReportFormatter S-C.V2", (2700, 350))
        n_chatout = make_node(chat_out, "ChatOutput", (3150, 350))

        nodes = [n_chatin, n_cfg, n_triage, n_capacity, n_eligibility, n_routing, n_qa, n_report, n_chatout]

        # Note: every target here is a LangFlow HandleInput, so the targetHandle
        # `type` field is "other" regardless of whether the accepted type is
        # Message or Data. (MessageTextInput and similar use "str", but we don't
        # use those.) An earlier version got 3 edges silently dropped because
        # it mismatched on this.
        edges = [
            # ChatInput -> PipelineConfig (Message)
            make_edge(n_chatin, "message", ["Message"],
                      n_cfg, "user_message", ["Message"], target_type="other"),
            # PipelineConfig -> TriageAgent (Data, run_config)
            make_edge(n_cfg, "run_config", ["Data"],
                      n_triage, "run_config", ["Data"], target_type="other"),
            # Triage -> Eligibility (Data)
            make_edge(n_triage, "scored_cases", ["Data"],
                      n_eligibility, "scored_cases", ["Data"], target_type="other"),
            # Eligibility -> Routing (Data)
            make_edge(n_eligibility, "eligible_cases", ["Data"],
                      n_routing, "eligible_cases", ["Data"], target_type="other"),
            # CapacityAdvisor -> Routing (Message)
            make_edge(n_capacity, "advisory", ["Message"],
                      n_routing, "capacity_advisory", ["Message"], target_type="other"),
            # Routing -> QA (Data)
            make_edge(n_routing, "assignments", ["Data"],
                      n_qa, "routing_output", ["Data"], target_type="other"),
            # QA -> Report (Data)
            make_edge(n_qa, "reviewed", ["Data"],
                      n_report, "reviewed", ["Data"], target_type="other"),
            # Report -> ChatOutput (Message — ChatOutput's input_value accepts
            # Data | JSON | DataFrame | Table | Message)
            make_edge(n_report, "report", ["Message"],
                      n_chatout, "input_value", ["Message"], target_type="other"),
        ]

        flow_payload = {
            "name": args.name,
            "description": "Scenario C v2: 6-agent multi-step routing flow.",
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.5},
            },
        }

        # Save to disk
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(flow_payload, indent=2) + "\n")
        print(f"=> saved {out_path.relative_to(Path.cwd())} ({out_path.stat().st_size:,} bytes)")

        if args.no_upload:
            print("=> --no-upload set; not posting to LangFlow")
            return 0

        # Delete previous copies with the same name so this is idempotent.
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
