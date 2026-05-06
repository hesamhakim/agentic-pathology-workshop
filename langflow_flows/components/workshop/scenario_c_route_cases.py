"""Scenario C — Digital Thread routing as a single LangFlow component.

Loads the lab state from data/scenario_c/, filters eligible pathologists per
case (subspecialty match + IHC capability + fatigue cap), asks an LLM to pick
one, and emits a markdown report. Each LLM call is automatically traced by
the LangFlow process's OTEL setup, so spans land in Phoenix.

The participant-editable knob is the `Fatigue Threshold` input on this node.
Default 999 (effectively no cap); set to 15 to see Dr. Jones (p002) and
Dr. Patel (p004) drop out of the eligible pool.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from langflow.custom import Component
from langflow.io import IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message
from openai import OpenAI


# Allow `from tools.scenario_c import ...` from inside the component.
_REPO_ROOT = Path("/workspaces/agentic-pathology-workshop")
if not _REPO_ROOT.exists():
    _REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


SYSTEM_PROMPT = """You are a pathology lab routing agent. Given a case and a list of
eligible pathologists with their current state, pick exactly one pathologist
to assign the case to. Optimize for: (1) subspecialty fit, (2) lowest current
queue depth, (3) availability window. Do NOT pick a pathologist outside the
provided eligible list.

Return ONLY a single JSON object with these keys:
  pathologist_id: string (must be one of the eligible ids)
  rationale: string (one sentence, concrete reasons, no hedging)

No markdown, no commentary, no surrounding text."""


def _route_one(client: OpenAI, model: str, case: dict, eligible: list[dict]) -> dict:
    user = json.dumps(
        {
            "case": {
                "id": case["id"],
                "requested_subspecialty": case["requested_subspecialty"],
                "priority": case["priority"],
                "requires_ihc": case["requires_ihc"],
                "specimen": case["specimen"],
                "patient_age": case.get("patient_age"),
            },
            "eligible_pathologists": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "subspecialties": p["subspecialties"],
                    "current_queue_depth": p["current_queue_depth"],
                    "available_until": p.get("available_until"),
                }
                for p in eligible
            ],
        }
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
        max_tokens=200,
    )
    return json.loads(resp.choices[0].message.content or "{}")


class RouteCases(Component):
    display_name = "Scenario C: Route Cases"
    description = (
        "Route incoming pathology cases to pathologists, respecting subspecialty, "
        "instrument availability, and the participant-editable fatigue cap."
    )
    icon = "split"
    name = "ScenarioC_RouteCases"

    inputs = [
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            value="data/scenario_c",
            info="Repo-relative path containing case_queue.json, instruments.json, pathologists.json, workload_history.json",
        ),
        IntInput(
            name="fatigue_threshold",
            display_name="Fatigue Threshold (avg slides/day)",
            value=999,
            info="Pathologists whose 7-day average meets or exceeds this are dropped. 999=no cap; 15=workshop's recommended value.",
        ),
        IntInput(
            name="lookback_days",
            display_name="Fatigue Lookback Days",
            value=7,
        ),
        IntInput(
            name="max_cases",
            display_name="Max Cases To Route",
            value=10,
            info="Limit to keep the workshop demo cheap. Cases are processed in stat→urgent→routine order.",
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o-mini",
        ),
        MultilineInput(
            name="system_prompt_override",
            display_name="System Prompt Override",
            value="",
            info="Leave blank to use the default routing prompt; paste a custom one to experiment.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Assignment Report", name="report", method="run_routing"),
    ]

    def _resolve_paths(self) -> dict[str, Path]:
        base = _REPO_ROOT / self.data_dir
        return {
            "cases": base / "case_queue.json",
            "instruments": base / "instruments.json",
            "pathologists": base / "pathologists.json",
            "workload": base / "workload_history.json",
        }

    def run_routing(self) -> Message:
        from tools.scenario_c import (
            case_queue,
            fatigue_cap,
            instrument_telemetry as inst,
            pathologist_registry as reg,
        )

        # Apply the threshold from the node input to the module-level rule
        # so attendees can tweak it on the canvas without editing fatigue_cap.py.
        fatigue_cap.DAILY_SLIDE_THRESHOLD = int(self.fatigue_threshold)
        fatigue_cap.LOOKBACK_DAYS = int(self.lookback_days)
        if self.system_prompt_override.strip():
            global SYSTEM_PROMPT  # noqa: PLW0603
            SYSTEM_PROMPT = self.system_prompt_override.strip()

        paths = self._resolve_paths()
        cases = case_queue.unassigned(case_queue.load(paths["cases"]))
        instruments = inst.load(paths["instruments"])
        pathologists = reg.load_pathologists(paths["pathologists"])
        history = reg.load_workload(paths["workload"])

        client = OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", "http://keybroker:8000/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

        ihc_available = inst.can_run_ihc(instruments)
        ordered = case_queue.by_priority(cases)[: int(self.max_cases)]

        lines = [
            f"# Routing report — {len(ordered)} of {len(cases)} unassigned case(s)",
            f"",
            f"- IHC capacity: **{'available' if ihc_available else 'UNAVAILABLE — IHC cases will be rejected'}**",
            f"- Fatigue threshold: **{self.fatigue_threshold}** (avg slides/day, {self.lookback_days}-day lookback)",
            f"",
            f"| # | Case | Sub-spec | Pri | IHC? | → Pathologist | Rationale |",
            f"|---|---|---|---|---|---|---|",
        ]

        skipped: list[tuple[str, str]] = []
        for idx, case in enumerate(ordered, start=1):
            if case["requires_ihc"] and not ihc_available:
                skipped.append((case["id"], "no IHC stainer online"))
                lines.append(f"| {idx} | {case['id']} | {case['requested_subspecialty']} | {case['priority']} | yes | — | _SKIPPED: no IHC capacity_ |")
                continue

            pool = reg.by_subspecialty(pathologists, case["requested_subspecialty"])
            survivors = fatigue_cap.filter_capped([p["id"] for p in pool], history)
            eligible = [p for p in pool if p["id"] in survivors]
            if not eligible:
                skipped.append((case["id"], f"no eligible pathologist after fatigue filter for {case['requested_subspecialty']}"))
                lines.append(f"| {idx} | {case['id']} | {case['requested_subspecialty']} | {case['priority']} | {'yes' if case['requires_ihc'] else 'no'} | — | _SKIPPED: pool empty_ |")
                continue

            try:
                decision = _route_one(client, self.model, case, eligible)
            except Exception as e:
                lines.append(f"| {idx} | {case['id']} | {case['requested_subspecialty']} | {case['priority']} | {'yes' if case['requires_ihc'] else 'no'} | — | _ERROR: {e}_ |")
                continue

            pid = decision.get("pathologist_id", "?")
            who = next((p for p in eligible if p["id"] == pid), None)
            who_name = who["name"] if who else f"unknown ({pid})"
            lines.append(
                f"| {idx} | {case['id']} | {case['requested_subspecialty']} | {case['priority']} | "
                f"{'yes' if case['requires_ihc'] else 'no'} | {who_name} ({pid}) | "
                f"{decision.get('rationale', '').replace('|', '/')} |"
            )

        if skipped:
            lines.append("")
            lines.append(f"**Skipped:** {len(skipped)} case(s) — {', '.join(f'{cid} ({why})' for cid, why in skipped[:5])}")

        return Message(text="\n".join(lines))
