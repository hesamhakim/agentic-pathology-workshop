"""Scenario C v2 — ReportFormatter.

Pure-Python step. Takes the QA-reviewed assignments and renders them in one
of five formats: markdown, csv, json, narrative, html. The format dropdown is
a single attendee knob that radically changes the output without touching
any other node — a clean way to show 'agentic workflows produce structured
intermediate state; the final renderer is just presentation'.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from langflow.custom import Component
from langflow.io import HandleInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message


VALID_FORMATS = {"markdown", "csv", "json", "narrative", "html"}


def _row_for_case(case: dict[str, Any], assignment: dict[str, Any] | None, flag: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "case_id": case["id"],
        "subspecialty": case["requested_subspecialty"],
        "priority": case["priority"],
        "priority_score": case.get("priority_score", ""),
        "requires_ihc": case["requires_ihc"],
        "specimen": case["specimen"],
        "patient_age": case.get("patient_age", ""),
        "pathologist_id": (assignment or {}).get("pathologist_id") or "",
        "rationale": (assignment or {}).get("rationale", ""),
        "qa_flag_severity": (flag or {}).get("severity", ""),
        "qa_flag_concern": (flag or {}).get("concern", ""),
    }


def _render_markdown(rows: list[dict[str, Any]], advisory: str) -> str:
    out = ["# Scenario C v2 — routing report", ""]
    if advisory:
        out += ["## Capacity advisory", "", advisory, ""]
    out += ["## Assignments", ""]
    out += ["| # | Case | Sub-spec | Pri | Score | IHC | → Pathologist | Rationale | QA Flag |"]
    out += ["|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        flag = f"{r['qa_flag_severity']}: {r['qa_flag_concern']}" if r['qa_flag_severity'] else ""
        out.append(
            f"| {i} | {r['case_id']} | {r['subspecialty']} | {r['priority']} | "
            f"{r['priority_score']} | {'yes' if r['requires_ihc'] else 'no'} | "
            f"{r['pathologist_id']} | {r['rationale']} | {flag} |"
        )
    return "\n".join(out)


def _render_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def _render_json(rows: list[dict[str, Any]], advisory: str) -> str:
    return json.dumps({"advisory": advisory, "assignments": rows}, indent=2, default=str)


def _render_narrative(rows: list[dict[str, Any]], advisory: str) -> str:
    parts = []
    if advisory:
        parts.append(f"Today's lab capacity advisory: {advisory}\n")
    parts.append(f"This routing run produced {len(rows)} assignment(s).")
    for r in rows:
        flag = f" QA flagged this ({r['qa_flag_severity']}): {r['qa_flag_concern']}." if r['qa_flag_severity'] else ""
        pid = r["pathologist_id"] or "UNASSIGNED"
        parts.append(
            f"\n- {r['case_id']} ({r['priority']}, {r['subspecialty']}, score={r['priority_score']}): "
            f"routed to {pid}. {r['rationale']}{flag}"
        )
    return "".join(parts)


def _render_html(rows: list[dict[str, Any]], advisory: str) -> str:
    body = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Scenario C v2 — routing report</title>",
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#111}"
        "h1{margin-bottom:4px}h2{color:#444;margin-top:24px}"
        "table{border-collapse:collapse;width:100%;font-size:14px}"
        "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}"
        "th{background:#f4f4f4}"
        ".flag-low{background:#fffbe6}.flag-medium{background:#ffe9d1}.flag-high{background:#ffd5d1}"
        "</style></head><body>",
        "<h1>Scenario C v2 — routing report</h1>",
    ]
    if advisory:
        body.append("<h2>Capacity advisory</h2>")
        body.append(f"<p>{advisory}</p>")
    body.append("<h2>Assignments</h2>")
    body.append("<table><tr>"
                "<th>#</th><th>Case</th><th>Sub-spec</th><th>Pri</th><th>Score</th>"
                "<th>IHC</th><th>Pathologist</th><th>Rationale</th><th>QA Flag</th></tr>")
    for i, r in enumerate(rows, 1):
        sev = r['qa_flag_severity']
        cls = f" class='flag-{sev}'" if sev else ""
        flag_cell = f"{sev}: {r['qa_flag_concern']}" if sev else ""
        body.append(
            f"<tr{cls}><td>{i}</td><td>{r['case_id']}</td><td>{r['subspecialty']}</td>"
            f"<td>{r['priority']}</td><td>{r['priority_score']}</td>"
            f"<td>{'yes' if r['requires_ihc'] else 'no'}</td>"
            f"<td>{r['pathologist_id'] or '—'}</td><td>{r['rationale']}</td>"
            f"<td>{flag_cell}</td></tr>"
        )
    body.append("</table></body></html>")
    return "\n".join(body)


class ScenarioC_v2_ReportFormatter(Component):
    display_name = "Report Formatter"
    description = (
        "Pure-Python renderer. Takes QA-reviewed assignments and emits one of: "
        "markdown, csv, json, narrative, html. The Format dropdown is the easiest "
        "attendee knob to demonstrate 'structured intermediate state, presentation last'."
    )
    icon = "file-text"
    name = "ReportFormatter S-C.V2"

    inputs = [
        HandleInput(
            name="reviewed",
            display_name="Reviewed Output",
            input_types=["Data"],
            info="Connect the QA Reviewer's output.",
        ),
        StrInput(
            name="format",
            display_name="Format",
            value="markdown",
            info="One of: markdown, csv, json, narrative, html.",
        ),
        MultilineInput(
            name="header_note",
            display_name="Header Note (optional)",
            value="",
            info="Prepended to markdown / narrative / html outputs.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Report", name="report", method="run_format"),
    ]

    def run_format(self) -> Message:
        data = self.reviewed.data
        cases = data.get("cases", [])
        assignments_by_case = {a["case_id"]: a for a in data.get("assignments", [])}
        flags_by_case = {f["case_id"]: f for f in data.get("flags", [])}
        advisory = data.get("advisory", "")
        run_config = data.get("run_config", {})

        rows = [
            _row_for_case(c, assignments_by_case.get(c["id"]), flags_by_case.get(c["id"]))
            for c in cases
        ]

        # Prefer format from upstream run_config; fall back to UI input.
        fmt = (run_config.get("format") or self.format or "markdown").strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(f"Format must be one of {sorted(VALID_FORMATS)}, got {fmt!r}")

        if fmt == "markdown":
            text = _render_markdown(rows, advisory)
        elif fmt == "csv":
            text = _render_csv(rows)
        elif fmt == "json":
            text = _render_json(rows, advisory)
        elif fmt == "narrative":
            text = _render_narrative(rows, advisory)
        elif fmt == "html":
            text = _render_html(rows, advisory)

        if self.header_note and fmt in {"markdown", "narrative"}:
            text = self.header_note.strip() + "\n\n" + text
        elif self.header_note and fmt == "html":
            text = text.replace("<body>", f"<body><p><em>{self.header_note}</em></p>")

        return Message(text=text)
