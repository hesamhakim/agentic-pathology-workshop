"""Scenario C v2 — EligibilityFilter.

Pure-Python rule-based step. Takes the triaged cases and narrows each one's
eligible pathologist pool by:
  - subspecialty match (toggleable for experimentation)
  - IHC capability of the lab (toggleable)
  - the participant-editable fatigue threshold

This component deliberately does NOT call an LLM. The pedagogical message is
'rules and LLMs cooperate'; the routing agent is more useful when fed a small,
already-filtered candidate list.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import BoolInput, HandleInput, IntInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_c.v2_helpers import DEFAULT_DATA_DIR, resolve_data_dir


class ScenarioC_v2_EligibilityFilter(Component):
    display_name = "Eligibility Filter"
    description = (
        "Pure-Python step. Combines subspecialty match + IHC capacity + the fatigue cap to "
        "produce a small eligible-pathologist list per case. The fatigue threshold is the "
        "workshop's headline EDIT ME knob."
    )
    icon = "filter"
    name = "EligibilityFilter S-C.V2"

    inputs = [
        HandleInput(
            name="scored_cases",
            display_name="Scored Cases",
            input_types=["Data"],
            info="Connect the Triage Agent's output here.",
        ),
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            value=DEFAULT_DATA_DIR,
            advanced=True,
        ),
        IntInput(
            name="fatigue_threshold",
            display_name="Fatigue Threshold (avg slides/day)",
            value=999,
            info="Pathologists whose recent average meets/exceeds this are dropped. 999=no cap; 15=workshop's recommended setting.",
        ),
        IntInput(
            name="lookback_days",
            display_name="Fatigue Lookback Days",
            value=7,
            advanced=True,
        ),
        BoolInput(
            name="enforce_subspecialty_match",
            display_name="Enforce Subspecialty Match",
            value=True,
            info="If off, any pathologist may receive any case (useful to demonstrate why subspecialty matters).",
        ),
        BoolInput(
            name="enforce_ihc_capacity",
            display_name="Enforce IHC Capacity",
            value=True,
            info="If off, IHC-required cases get assigned even when no IHC stainer is online.",
        ),
        IntInput(
            name="ihc_min_reagent_pct",
            display_name="IHC Min Reagent %",
            value=10,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Cases With Eligible Pool", name="eligible_cases", method="run_filter"),
    ]

    def run_filter(self) -> Data:
        from tools.scenario_c import (
            instrument_telemetry,
            pathologist_registry as reg,
        )

        base = resolve_data_dir(self.data_dir)
        instruments = instrument_telemetry.load(base / "instruments.csv")
        pathologists = reg.load_pathologists(base / "pathologists.csv")
        history = reg.load_workload(base / "workload_history.csv")

        cases = self.scored_cases.data.get("cases", [])
        ihc_capable = instrument_telemetry.can_run_ihc(instruments, self.ihc_min_reagent_pct)

        out_cases = []
        for case in cases:
            pool = list(pathologists)
            if self.enforce_subspecialty_match:
                pool = reg.by_subspecialty(pool, case["requested_subspecialty"])
            if self.enforce_ihc_capacity and case["requires_ihc"] and not ihc_capable:
                pool = []
            # Apply fatigue cap.
            pool = [
                p for p in pool
                if reg.recent_load_avg(history, p["id"], days=self.lookback_days) < self.fatigue_threshold
            ]
            out_cases.append({
                **case,
                "eligible_pathologists": [
                    {"id": p["id"], "name": p["name"], "current_queue_depth": p["current_queue_depth"]}
                    for p in pool
                ],
            })

        return Data(data={
            "cases": out_cases,
            "stats": {
                "ihc_capable": ihc_capable,
                "fatigue_threshold": self.fatigue_threshold,
                "subspecialty_enforced": self.enforce_subspecialty_match,
                "ihc_enforced": self.enforce_ihc_capacity,
            },
        })
