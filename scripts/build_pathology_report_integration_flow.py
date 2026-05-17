#!/usr/bin/env python3
"""Build the pathology_report_integration flow programmatically.

This is the post-refactor (2026-05-16) successor to
build_scenario_d_v2_flow.py. The flow has a fan-out / fan-in shape
that makes the per-modality nature of integrated reporting visible:

  ChatInput -> PipelineConfig -> PDFIntake (5 outputs):
    morphology_data    -> MorphologyParser    -+
    flow_data          -> FlowParser          -+
    cytogenetics_data  -> CytogeneticsParser  -+-> WHOClassifier -> QAReviewer -> ReportFormatter -> ChatOutput
    molecular_data     -> MolecularParser     -+        ^
    cross_report_data  ----------------------- (^)      |
                                                 [WHO Instructions]
                                                 (TextInput, prefilled
                                                  with docs/who5e_instructions.md)

11 nodes total: 1 ChatInput + 1 ChatOutput + 8 custom Scenario-D
components + 1 stock TextInput (WHO Instructions). 15 edges.

The WHO Instructions text loads its default from
docs/who5e_instructions.md so the file is the single source of
truth that attendees, facilitators, and slides all reference.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

import httpx


REPO_ROOT = Path(__file__).resolve().parents[1]
WHO_INSTRUCTIONS_PATH = REPO_ROOT / "docs" / "who5e_instructions.md"
LF_QUOTE = "œ"


def encode_handle(d: dict) -> str:
    return json.dumps(d, separators=(",", ":")).replace('"', LF_QUOTE)


def login(client: httpx.Client) -> str:
    import os
    user = os.environ.get("WORKSHOP_LF_USER", "facilitator")
    pw = os.environ.get("WORKSHOP_LF_PASSWORD", "workshop-admin-2026")
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
        raise SystemExit(
            f"category {category!r} not in registry. "
            f"Available: {sorted(all_components)[:15]}"
        )
    if name not in all_components[category]:
        raise SystemExit(
            f"component {name!r} not in {category!r}. "
            f"Available: {sorted(all_components[category])}"
        )
    return all_components[category][name]


def make_node(template: dict, component_name: str, position: tuple[float, float],
              field_overrides: dict | None = None) -> dict:
    import copy
    tpl = copy.deepcopy(template)
    if field_overrides:
        fields = tpl.setdefault("template", {})
        for k, v in field_overrides.items():
            if k in fields and isinstance(fields[k], dict):
                fields[k]["value"] = v
    node_id = f"{component_name.replace(' ', '_')}-{secrets.token_hex(3)}"
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": position[0], "y": position[1]},
        "data": {
            "id": node_id,
            "type": component_name,
            "node": tpl,
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


def load_who_instructions() -> str:
    if not WHO_INSTRUCTIONS_PATH.exists():
        raise SystemExit(
            f"WHO instructions source not found at {WHO_INSTRUCTIONS_PATH}. "
            "Restore docs/who5e_instructions.md before building."
        )
    return WHO_INSTRUCTIONS_PATH.read_text()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:7860")
    parser.add_argument("--name", default="pathology_report_integration")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    out_path = REPO_ROOT / "langflow_flows" / "pathology_report_integration.json"
    who_text = load_who_instructions()

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        cat_d = "api_scenario_d"
        cat_io = "input_output"

        # ---- component templates ----
        chat_in_tpl   = get_component(all_components, cat_io, "ChatInput")
        cfg_tpl       = get_component(all_components, cat_d, "PipelineConfig S-D.V2")
        intake_tpl    = get_component(all_components, cat_d, "PDFIntake S-D.V2")
        morph_tpl     = get_component(all_components, cat_d, "MorphologyParser S-D.V2")
        flow_tpl      = get_component(all_components, cat_d, "FlowParser S-D.V2")
        cyto_tpl      = get_component(all_components, cat_d, "CytogeneticsParser S-D.V2")
        mol_tpl       = get_component(all_components, cat_d, "MolecularParser S-D.V2")
        who_text_tpl  = get_component(all_components, cat_io, "TextInput")
        classifier_tpl = get_component(all_components, cat_d, "WHOClassifier S-D.V2")
        qa_tpl        = get_component(all_components, cat_d, "QAReviewer S-D.V2")
        report_tpl    = get_component(all_components, cat_d, "ReportFormatter S-D.V2")
        chat_out_tpl  = get_component(all_components, cat_io, "ChatOutput")

        # ---- layout (1920px-wide deck-friendly) ----
        # Left column: ChatInput -> PipelineConfig -> PDFIntake
        # Middle column: 4 parsers stacked + WHO Instructions
        # Right column: WHOClassifier -> QAReviewer -> ReportFormatter -> ChatOutput
        n_chatin   = make_node(chat_in_tpl,    "ChatInput",                  (50,   500))
        n_cfg      = make_node(cfg_tpl,        "PipelineConfig S-D.V2",      (450,  500))
        n_intake   = make_node(intake_tpl,     "PDFIntake S-D.V2",           (900,  500))

        n_morph    = make_node(morph_tpl,      "MorphologyParser S-D.V2",    (1500, 50))
        n_flow     = make_node(flow_tpl,       "FlowParser S-D.V2",          (1500, 300))
        n_cyto     = make_node(cyto_tpl,       "CytogeneticsParser S-D.V2",  (1500, 550))
        n_mol      = make_node(mol_tpl,        "MolecularParser S-D.V2",     (1500, 800))
        n_who_text = make_node(
            who_text_tpl, "TextInput", (1500, 1050),
            field_overrides={"input_value": who_text},
        )

        n_classifier = make_node(classifier_tpl, "WHOClassifier S-D.V2",     (2100, 500))
        n_qa         = make_node(qa_tpl,         "QAReviewer S-D.V2",        (2650, 500))
        n_report     = make_node(report_tpl,     "ReportFormatter S-D.V2",   (3200, 500))
        n_chatout    = make_node(chat_out_tpl,   "ChatOutput",               (3750, 500))

        nodes = [
            n_chatin, n_cfg, n_intake,
            n_morph, n_flow, n_cyto, n_mol, n_who_text,
            n_classifier, n_qa, n_report, n_chatout,
        ]

        edges = [
            # ChatInput -> PipelineConfig
            make_edge(n_chatin, "message", ["Message"], n_cfg, "user_message", ["Message"]),
            # PipelineConfig -> PDFIntake
            make_edge(n_cfg, "run_config", ["Data"], n_intake, "run_config", ["Data"]),

            # PDFIntake -> 4 parsers (per-source fan-out)
            make_edge(n_intake, "morphology_data",   ["Data"], n_morph, "morphology_data",   ["Data"]),
            make_edge(n_intake, "flow_data",         ["Data"], n_flow,  "flow_data",         ["Data"]),
            make_edge(n_intake, "cytogenetics_data", ["Data"], n_cyto,  "cytogenetics_data", ["Data"]),
            make_edge(n_intake, "molecular_data",    ["Data"], n_mol,   "molecular_data",    ["Data"]),
            # PDFIntake cross_report_data -> WHOClassifier directly (skips parsers)
            make_edge(n_intake, "cross_report_data", ["Data"], n_classifier, "cross_report", ["Data"]),

            # 4 parsers -> WHOClassifier (fan-in)
            make_edge(n_morph, "morphology_synthesis",  ["Message"], n_classifier, "morphology_synthesis",  ["Message"]),
            make_edge(n_flow,  "flow_synthesis",        ["Message"], n_classifier, "flow_synthesis",        ["Message"]),
            make_edge(n_cyto,  "cytogenetics_synthesis",["Message"], n_classifier, "cytogenetics_synthesis",["Message"]),
            make_edge(n_mol,   "molecular",             ["Data"],    n_classifier, "molecular",             ["Data"]),

            # WHO Instructions -> WHOClassifier (sixth input)
            make_edge(n_who_text, "text", ["Message"], n_classifier, "who_instructions", ["Message"]),

            # Tail: WHOClassifier -> QA -> Formatter -> ChatOutput
            make_edge(n_classifier, "integrated", ["Data"],    n_qa,        "integrated",  ["Data"]),
            make_edge(n_qa,         "reviewed",   ["Data"],    n_report,    "reviewed",    ["Data"]),
            make_edge(n_report,     "report",     ["Message"], n_chatout,   "input_value", ["Message"]),
        ]

        flow_payload = {
            "name": args.name,
            "description": (
                "Pathology Report Integration — Stage-1 PDF Intake fans out into "
                "four per-modality parsers (morphology, flow, cytogenetics, "
                "molecular) plus a cross-report observations channel. A separate "
                "WHO Instructions Text Input feeds official WHO 5e classification "
                "rules into the Stage-2 WHO Classifier without modifying the "
                "integrator's own system prompt. Run `run the aml case` in "
                "Playground to exercise the full pipeline."
            ),
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.35},
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
