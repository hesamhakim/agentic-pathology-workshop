#!/usr/bin/env python3
"""Build the A_variant_tournament flow programmatically.

Mirrors scripts/build_scenario_c_v2_flow.py — same edge-encoding helpers,
same upload-and-save pattern.

Wiring:
  ChatInput -> PipelineConfig -> VariantTriage \
                                                  EvidenceAggregator -> TournamentJudge -> QAReviewer -> ReportFormatter -> ChatOutput
                              EvidenceAdvisor (parallel branch) ___________^
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
        "type": "other",  # always 'other' for HandleInput-style targets
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
    parser.add_argument("--name", default="A_variant_tournament")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    out_path = Path(__file__).resolve().parents[1] / "langflow_flows" / "A_variant_tournament.json"

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        cat_a = "api_scenario_a"
        cat_io = "input_output"

        chat_in = get_component(all_components, cat_io, "ChatInput")
        cfg = get_component(all_components, cat_a, "PipelineConfig S-A.V2")
        triage = get_component(all_components, cat_a, "VariantTriage S-A.V2")
        advisor = get_component(all_components, cat_a, "EvidenceAdvisor S-A.V2")
        aggregator = get_component(all_components, cat_a, "EvidenceAggregator S-A.V2")
        judge = get_component(all_components, cat_a, "TournamentJudge S-A.V2")
        qa = get_component(all_components, cat_a, "QAReviewer S-A.V2")
        report = get_component(all_components, cat_a, "ReportFormatter S-A.V2")
        chat_out = get_component(all_components, cat_io, "ChatOutput")

        n_chatin = make_node(chat_in, "ChatInput", (50, 250))
        n_cfg = make_node(cfg, "PipelineConfig S-A.V2", (450, 250))
        n_triage = make_node(triage, "VariantTriage S-A.V2", (900, 100))
        n_advisor = make_node(advisor, "EvidenceAdvisor S-A.V2", (900, 600))
        n_aggregator = make_node(aggregator, "EvidenceAggregator S-A.V2", (1350, 100))
        n_judge = make_node(judge, "TournamentJudge S-A.V2", (1800, 350))
        n_qa = make_node(qa, "QAReviewer S-A.V2", (2250, 350))
        n_report = make_node(report, "ReportFormatter S-A.V2", (2700, 350))
        n_chatout = make_node(chat_out, "ChatOutput", (3150, 350))

        nodes = [n_chatin, n_cfg, n_triage, n_advisor, n_aggregator, n_judge, n_qa, n_report, n_chatout]

        edges = [
            # ChatInput -> PipelineConfig (Message)
            make_edge(n_chatin, "message", ["Message"], n_cfg, "user_message", ["Message"]),
            # PipelineConfig -> VariantTriage (Data, run_config)
            make_edge(n_cfg, "run_config", ["Data"], n_triage, "run_config", ["Data"]),
            # VariantTriage -> EvidenceAggregator (Data)
            make_edge(n_triage, "scored_variants", ["Data"], n_aggregator, "scored_variants", ["Data"]),
            # EvidenceAggregator -> TournamentJudge (Data)
            make_edge(n_aggregator, "aggregated", ["Data"], n_judge, "aggregated", ["Data"]),
            # EvidenceAdvisor -> TournamentJudge (Message)
            make_edge(n_advisor, "advisory", ["Message"], n_judge, "clinical_context", ["Message"]),
            # TournamentJudge -> QAReviewer (Data)
            make_edge(n_judge, "ranked", ["Data"], n_qa, "judge_output", ["Data"]),
            # QAReviewer -> ReportFormatter (Data)
            make_edge(n_qa, "reviewed", ["Data"], n_report, "reviewed", ["Data"]),
            # ReportFormatter -> ChatOutput (Message)
            make_edge(n_report, "report", ["Message"], n_chatout, "input_value", ["Message"]),
        ]

        flow_payload = {
            "name": args.name,
            "description": "Scenario A v2: 6-agent variant tournament with phenopacket export.",
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
