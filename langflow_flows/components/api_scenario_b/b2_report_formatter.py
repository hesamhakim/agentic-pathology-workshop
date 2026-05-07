"""Scenario B v2 — Report Formatter."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from langflow.custom import Component
from langflow.io import HandleInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message


VALID_FORMATS = {"markdown", "csv", "json", "narrative", "html"}


def _row(f: dict[str, Any], qa_flag: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "id": f.get("id", ""),
        "severity": f.get("severity", ""),
        "topic": f.get("topic", ""),
        "claim": f.get("claim", ""),
        "explanation": f.get("explanation", ""),
        "evidence_note_ids": ";".join(f.get("evidence_note_ids", [])),
        "qa_concern": (qa_flag or {}).get("concern", "") if qa_flag else "",
        "qa_severity": (qa_flag or {}).get("severity", "") if qa_flag else "",
        "qa_comment": (qa_flag or {}).get("comment", "") if qa_flag else "",
    }


def _md(rows: list[dict[str, Any]], sdoh: list[dict[str, Any]], request: dict[str, Any]) -> str:
    out = ["# Longitudinal ghost — chart-vs-request reconciliation", ""]
    out += [f"**Request id:** {request.get('request_id', '?')}  ",
            f"**Specimen:** {request.get('specimen', '?')}  ",
            f"**Requesting provider:** {request.get('requesting_provider', '?')}", ""]
    out += [f"## Findings ({len(rows)})", ""]
    if not rows:
        out.append("_No contradictions identified._")
    else:
        out += ["| # | Severity | Topic | Claim | Explanation | Evidence | QA Flag |",
                "|---|---|---|---|---|---|---|"]
        for i, r in enumerate(rows, 1):
            qa = f"{r['qa_severity']}: {r['qa_concern']}" if r['qa_concern'] else ""
            out.append(
                f"| {i} | {r['severity']} | {r['topic']} | {r['claim']} | "
                f"{r['explanation']} | {r['evidence_note_ids']} | {qa} |"
            )
    if sdoh:
        out += ["", f"## SDoH context ({len(sdoh)})", ""]
        out += ["| # | Category | Finding | Evidence |", "|---|---|---|---|"]
        for i, s in enumerate(sdoh, 1):
            ev = ";".join(s.get("evidence_note_ids", []))
            out.append(f"| {i} | {s.get('category','')} | {s.get('finding','')} | {ev} |")
    return "\n".join(out)


def _csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def _json(rows: list[dict[str, Any]], sdoh: list[dict[str, Any]], request: dict[str, Any]) -> str:
    return json.dumps({"request": request, "findings": rows, "sdoh": sdoh}, indent=2, default=str)


def _narrative(rows: list[dict[str, Any]], sdoh: list[dict[str, Any]]) -> str:
    parts = [f"Reviewing the current pathology request against the chart, {len(rows)} contradiction(s) were identified."]
    for r in rows:
        qa = f" QA-{r['qa_severity']}: {r['qa_concern']}." if r['qa_concern'] else ""
        parts.append(
            f"\n[{r['severity'].upper()}] {r['topic']} — claim: \"{r['claim']}\". {r['explanation']} "
            f"(see {r['evidence_note_ids']}).{qa}"
        )
    if sdoh:
        parts.append(f"\n\nSocial-determinant context worth noting:")
        for s in sdoh:
            parts.append(f"\n- {s.get('category','')}: {s.get('finding','')}.")
    return "".join(parts)


def _html(rows: list[dict[str, Any]], sdoh: list[dict[str, Any]], request: dict[str, Any]) -> str:
    body = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Longitudinal ghost — reconciliation</title>",
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1080px;margin:24px auto;padding:0 16px;color:#111}"
        "h1{margin-bottom:4px}h2{color:#444;margin-top:24px}"
        "table{border-collapse:collapse;width:100%;font-size:13px}"
        "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}"
        "th{background:#f4f4f4}"
        ".sev-low{background:#fffbe6}.sev-medium{background:#ffe9d1}.sev-high{background:#ffd5d1}"
        "</style></head><body>",
        "<h1>Longitudinal ghost — reconciliation</h1>",
        f"<p><strong>Request:</strong> {request.get('request_id','?')} — {request.get('specimen','?')}<br>"
        f"<strong>Requesting provider:</strong> {request.get('requesting_provider','?')}</p>",
        f"<h2>Findings ({len(rows)})</h2>",
    ]
    if not rows:
        body.append("<p><em>No contradictions identified.</em></p>")
    else:
        body.append("<table><tr>"
                    "<th>#</th><th>Severity</th><th>Topic</th><th>Claim</th>"
                    "<th>Explanation</th><th>Evidence</th><th>QA</th></tr>")
        for i, r in enumerate(rows, 1):
            cls = f" class='sev-{r['severity']}'" if r['severity'] in {'low','medium','high'} else ""
            qa = f"{r['qa_severity']}: {r['qa_concern']}" if r['qa_concern'] else ""
            body.append(
                f"<tr{cls}><td>{i}</td><td>{r['severity']}</td>"
                f"<td>{r['topic']}</td><td>{r['claim']}</td><td>{r['explanation']}</td>"
                f"<td>{r['evidence_note_ids']}</td><td>{qa}</td></tr>"
            )
        body.append("</table>")
    if sdoh:
        body.append(f"<h2>SDoH context ({len(sdoh)})</h2><ul>")
        for s in sdoh:
            ev = ";".join(s.get("evidence_note_ids", []))
            body.append(f"<li><strong>{s.get('category','')}:</strong> {s.get('finding','')} <em>({ev})</em></li>")
        body.append("</ul>")
    body.append("</body></html>")
    return "\n".join(body)


class ScenarioB_v2_ReportFormatter(Component):
    display_name = "Report Formatter"
    description = (
        "Pure-Python renderer. Outputs markdown / csv / json / narrative / html. "
        "Picks up `format` override from the chat-input directive when connected upstream."
    )
    icon = "file-text"
    name = "ReportFormatter S-B.V2"

    inputs = [
        HandleInput(
            name="reviewed",
            display_name="Reviewed Output",
            input_types=["Data"],
            info="Connect the QA Reviewer output.",
        ),
        HandleInput(
            name="sdoh",
            display_name="SDoH Findings",
            input_types=["Data"],
            required=False,
            info="Optional. Connect the SDoH Extractor output to include a social-determinant section.",
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
            advanced=True,
        ),
    ]

    outputs = [Output(display_name="Report", name="report", method="run_format")]

    def run_format(self) -> Message:
        d = self.reviewed.data
        findings = d.get("findings", [])
        qa_flags = d.get("qa_flags", [])
        request = d.get("request", {})
        run_config = d.get("run_config", {})

        sdoh_list: list[dict[str, Any]] = []
        if self.sdoh is not None:
            sdoh_data = self.sdoh.data or {}
            if not sdoh_data.get("disabled"):
                sdoh_list = sdoh_data.get("sdoh", [])

        # Pair each finding with its QA flag (by finding_id)
        flag_by_id = {f.get("finding_id"): f for f in qa_flags if f.get("finding_id")}
        rows = [_row(f, flag_by_id.get(f.get("id"))) for f in findings]

        fmt = (run_config.get("format") or self.format or "markdown").strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(f"Format must be one of {sorted(VALID_FORMATS)}, got {fmt!r}")

        if fmt == "markdown":
            text = _md(rows, sdoh_list, request)
        elif fmt == "csv":
            text = _csv(rows)
        elif fmt == "json":
            text = _json(rows, sdoh_list, request)
        elif fmt == "narrative":
            text = _narrative(rows, sdoh_list)
        elif fmt == "html":
            text = _html(rows, sdoh_list, request)

        if self.header_note and fmt in {"markdown", "narrative"}:
            text = self.header_note.strip() + "\n\n" + text
        elif self.header_note and fmt == "html":
            text = text.replace("<body>", f"<body><p><em>{self.header_note}</em></p>")

        return Message(text=text)
