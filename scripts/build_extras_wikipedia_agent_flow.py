#!/usr/bin/env python3
"""Build the Research_Buddy reference flow programmatically.

A deliberately tiny agentic workflow assembled from STANDARD LangFlow
components only — no custom Python, no imports from /flows/components.
Workshop attendees build this from scratch as the "Build it yourself"
exercise; we ship this generated JSON so they can import it afterwards
and compare against the completed shape.

Topology:

    [Chat Input] ─► [Agent] ─► [Chat Output]
                     ▲ ▲
                     │ └─ Wikipedia API  (api_build_tool → tools)
                     └─── Calculator     (api_build_tool → tools)

All four components are present in LangFlow 1.9.2 (verified via
GET /api/v1/all on the workshop VM). The Agent's `model` field is
left empty by design — attendees pick OpenAI + gpt-4o-mini in the
node's right-side detail panel on first run. The OPENAI_API_KEY env
var (the attendee's broker token) and OPENAI_BASE_URL (the KeyBroker)
are already wired in the langflow container, so no API key needs to
be pasted.

Mirrors scripts/build_scenario_zero_flow.py — same encoding pattern,
same upload-and-save flow.
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
        raise SystemExit(f"category {category!r} not in registry")
    if name not in all_components[category]:
        raise SystemExit(
            f"component {name!r} not in {category!r}. "
            f"Available: {sorted(all_components[category])}"
        )
    return all_components[category][name]


def make_node(
    template: dict,
    component_name: str,
    position: tuple[float, float],
    field_overrides: dict | None = None,
) -> dict:
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


def enable_tool_mode(node: dict, action_name: str, action_description: str,
                     action_args: dict | None = None) -> None:
    """Convert a regular Component node into a tool-mode node.

    Tool-mode replaces the node's normal outputs with a single
    `component_as_tool: Tool` output that the Agent's `tools` handle
    accepts. The starter "Simple Agent" project does this for the
    Calculator; we mirror the exact same shape here so a non-legacy
    Wikipedia + non-legacy Calculator can both be wired as tools.
    """
    nd = node["data"]["node"]
    nd["tool_mode"] = True
    nd["outputs"] = [
        {
            "allows_loop": False,
            "cache": True,
            "display_name": "Toolset",
            "group_outputs": False,
            "hidden": False,
            "loop_types": None,
            "method": "to_toolkit",
            "name": "component_as_tool",
            "options": None,
            "required_inputs": None,
            "selected": "Tool",
            "tool_mode": True,
            "types": ["Tool"],
            "value": "__UNDEFINED__",
        }
    ]
    nd["template"]["tools_metadata"] = {
        "_input_type": "ToolsInput",
        "advanced": False,
        "display_name": "Actions",
        "dynamic": False,
        "info": (
            "Modify tool names and descriptions to help agents "
            "understand when to use each tool."
        ),
        "is_list": True,
        "list_add_label": "Add More",
        "name": "tools_metadata",
        "override_skip": False,
        "placeholder": "",
        "real_time_refresh": True,
        "required": False,
        "show": True,
        "title_case": False,
        "tool_mode": False,
        "trace_as_metadata": True,
        "track_in_telemetry": False,
        "type": "tools",
        "value": [
            {
                "args": action_args or {},
                "description": action_description,
                "display_description": action_description,
                "display_name": action_name,
                "name": action_name,
                "status": True,
                "tags": [action_name],
            }
        ],
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


RESEARCH_BUDDY_INSTRUCTIONS = (
    "You are a helpful research assistant. "
    "When the user asks a factual question, use the Wikipedia API to look it up. "
    "When the user asks anything requiring arithmetic, use the Calculator. "
    "If a question needs both — for example, 'what's the population of Tokyo "
    "divided by the population of Osaka?' — call the tools in sequence and "
    "show your reasoning step by step. "
    "When you cite a Wikipedia fact, mention the article you used."
)


# Pre-configures the Agent node's "Language Model" dropdown so the
# shipped JSON runs without manual setup. Verified end-to-end against
# the workshop VM's KeyBroker proxy on 2026-05-16: the agent picks the
# right tool, the broker forwards the call to OpenRouter, and a reply
# comes back. Attendees building from scratch will instead select
# OpenAI + gpt-4o-mini in the node's right-side detail panel.
DEFAULT_AGENT_MODEL = [
    {
        "name": "openai/gpt-4o-mini",
        "icon": "OpenAI",
        "category": "OpenAI",
        "provider": "OpenAI",
        "metadata": {
            "context_length": 128000,
            "model_class": "ChatOpenAI",
            "model_name_param": "model",
            "api_key_param": "api_key",
        },
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:7860")
    parser.add_argument("--name", default="extras_wikipedia_agent")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    out_path = (
        Path(__file__).resolve().parents[1]
        / "langflow_flows"
        / "extras_wikipedia_agent.json"
    )

    with httpx.Client(base_url=args.host, timeout=60.0) as client:
        print("=> login")
        token = login(client)
        client.headers["Authorization"] = f"Bearer {token}"

        print("=> fetch component registry")
        all_components = fetch_all_components(client)

        chat_in_tpl = get_component(all_components, "input_output", "ChatInput")
        agent_tpl = get_component(all_components, "models_and_agents", "Agent")
        # NON-LEGACY tools. tools/WikipediaAPI and tools/CalculatorTool
        # are marked legacy in LangFlow 1.9.2; the canvas drops their
        # edges on load. Use the modern components with tool-mode
        # enabled — same pattern as LangFlow's built-in "Simple Agent"
        # starter project.
        wiki_tpl = get_component(all_components, "wikipedia", "WikipediaComponent")
        calc_tpl = get_component(all_components, "utilities", "CalculatorComponent")
        chat_out_tpl = get_component(all_components, "input_output", "ChatOutput")

        # Left-to-right layout. Tools sit below the Agent in a row of
        # two so attendees see the "agent has multiple tools" pattern
        # clearly on first load.
        n_chatin = make_node(chat_in_tpl, "ChatInput", (50, 300))
        n_agent = make_node(
            agent_tpl,
            "Agent",
            (600, 300),
            field_overrides={
                "system_prompt": RESEARCH_BUDDY_INSTRUCTIONS,
                "model": DEFAULT_AGENT_MODEL,
            },
        )
        n_wiki = make_node(wiki_tpl, "WikipediaComponent", (400, 700))
        enable_tool_mode(
            n_wiki,
            action_name="fetch_content",
            action_description=(
                "WikipediaComponent. fetch_content() - Search Wikipedia "
                "and return article summaries. Use this for factual "
                "lookups: people, places, populations, definitions, etc."
            ),
            action_args={
                "input_value": {
                    "default": "",
                    "description": "Search query for Wikipedia.",
                    "title": "Input",
                    "type": "string",
                },
            },
        )
        n_calc = make_node(calc_tpl, "CalculatorComponent", (800, 700))
        enable_tool_mode(
            n_calc,
            action_name="evaluate_expression",
            action_description=(
                "CalculatorComponent. evaluate_expression() - Perform "
                "basic arithmetic operations on a given expression."
            ),
            action_args={
                "expression": {
                    "default": "",
                    "description": (
                        "The arithmetic expression to evaluate "
                        "(e.g., '4*4*(33/22)+12-20')."
                    ),
                    "title": "Expression",
                    "type": "string",
                },
            },
        )
        n_chatout = make_node(chat_out_tpl, "ChatOutput", (1200, 300))

        nodes = [n_chatin, n_agent, n_wiki, n_calc, n_chatout]

        edges = [
            # Chat Input → Agent.input_value
            make_edge(
                n_chatin, "message", ["Message"],
                n_agent, "input_value", ["Message"],
            ),
            # Wikipedia (tool mode) → Agent.tools
            make_edge(
                n_wiki, "component_as_tool", ["Tool"],
                n_agent, "tools", ["Tool"],
            ),
            # Calculator (tool mode) → Agent.tools
            make_edge(
                n_calc, "component_as_tool", ["Tool"],
                n_agent, "tools", ["Tool"],
            ),
            # Agent.response → Chat Output
            make_edge(
                n_agent, "response", ["Message"],
                n_chatout, "input_value", ["Message"],
            ),
        ]

        flow_payload = {
            "name": args.name,
            "description": (
                "Research Buddy — a five-node reference workflow assembled "
                "from standard LangFlow components only (Chat Input, Agent, "
                "Wikipedia API, Calculator, Chat Output). Workshop attendees "
                "build this from scratch as the 'build it yourself' exercise; "
                "import this flow afterwards to compare against the completed "
                "shape. On first run, click the Agent node and pick OpenAI + "
                "gpt-4o-mini as the Language Model — leave API Key blank "
                "(the workshop's broker token is wired via the container "
                "OPENAI_API_KEY env var). Try: 'What's the population of "
                "Tokyo?', 'What is 23 percent of 7.8 million?', then 'What "
                "is the population of Tokyo divided by the population of "
                "Osaka?' to see the agent reason across both tools."
            ),
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.5},
            },
        }

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(flow_payload, indent=2) + "\n")
        size = out_path.stat().st_size
        print(f"=> saved {out_path.relative_to(Path.cwd())} ({size:,} bytes)")

        if args.no_upload:
            print("=> --no-upload set; skipping POST")
            return 0

        existing = client.get(
            "/api/v1/flows/", params={"page": 1, "size": 100}
        ).json()
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
