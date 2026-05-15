"""Scenario D v2 — ReportFormatter.

Pure-Python renderer for Omar's 11-section integrated report + Part B
evidence trace. Four output formats: integrated (markdown), narrative
(short paragraph), json (machine-readable), html. Reads format
override from upstream run_config so the chat directive picks the
output shape.
"""

from __future__ import annotations

import json
from typing import Any

from langflow.custom import Component
from langflow.io import HandleInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message


VALID_FORMATS = {"integrated", "narrative", "json", "html"}


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def _component_studies_md(studies: list[dict]) -> str:
    if not studies:
        return "_(no component studies reported)_"
    out = ["| Source | Lab | Accession | Reported |", "|---|---|---|---|"]
    for s in studies:
        out.append(
            f"| {s.get('source_id','')} | {s.get('lab','')} | "
            f"{s.get('accession','')} | {s.get('report_date','')} |"
        )
    return "\n".join(out)


def _evidence_trace_md(trace: list[dict]) -> str:
    if not trace:
        return "_(no evidence trace produced)_"
    out = ["| # | Section | Sentence | Source(s) | Basis |",
           "|---|---|---|---|---|"]
    for row in trace:
        section = row.get("section", "")
        n = row.get("sentence_number", "")
        sent = (row.get("sentence", "") or "").replace("|", "\\|")
        srcs = ", ".join(row.get("supporting_source_ids", []) or [])
        basis = row.get("basis", "")
        out.append(f"| {n} | {section} | {sent} | {srcs} | {basis} |")
    return "\n".join(out)


def _flags_md(flags: list[dict]) -> str:
    if not flags:
        return "_(no QA flags raised)_"
    out = []
    for f in flags:
        sev = (f.get("severity", "low") or "low").upper()
        cat = f.get("category", "")
        out.append(f"- **{sev}** [{cat}] — {f.get('concern','')}"
                   f" _({f.get('reference','')})_")
    return "\n".join(out)


# -------------------------------------------------------------------------
# Markdown integrated layout (Omar 11-section + Part B trace)
# -------------------------------------------------------------------------

def _integrated_md(d: dict[str, Any]) -> str:
    integrated = d.get("integrated_report", {}) or {}
    trace = d.get("evidence_trace", []) or []
    flags = d.get("flags", []) or []
    run_config = d.get("run_config", {}) or {}
    show_evidence = run_config.get("show_evidence", True)
    show_qa = run_config.get("show_qa", True)

    out = [f"# Integrated Diagnostic Report — {d.get('case_id', '')}", ""]
    out.append("**Part A — Integrated Report**")
    out.append("")
    out.append("## 1. Patient and specimen identification")
    out.append(integrated.get("patient_specimen_id", "") or "_(not provided)_")
    out.append("")
    out.append("## 2. Component studies reviewed")
    out.append(_component_studies_md(integrated.get("component_studies", []) or []))
    out.append("")
    out.append("## 3. Clinical context")
    out.append(integrated.get("clinical_context", "") or "_(not provided)_")
    out.append("")
    out.append("## 4. Morphology summary")
    out.append(integrated.get("morphology_summary", "") or "_(not applicable)_")
    out.append("")
    out.append("## 5. Flow / IHC summary")
    out.append(integrated.get("flow_or_ihc_summary", "") or "_(not applicable)_")
    out.append("")
    out.append("## 6. Cytogenetics summary")
    out.append(integrated.get("cytogenetics_summary", "") or "_(not applicable)_")
    out.append("")
    out.append("## 7. Molecular summary")
    out.append(integrated.get("molecular_summary", "") or "_(not applicable)_")
    out.append("")
    out.append("## 8. Integrated interpretation")
    for i, s in enumerate(integrated.get("integrated_interpretation", []) or [], 1):
        out.append(f"{i}. {s}")
    out.append("")
    out.append("## 9. Final integrated diagnosis")
    for i, s in enumerate(integrated.get("final_integrated_diagnosis", []) or [], 1):
        out.append(f"{i}. {s}")
    out.append("")
    out.append("## 10. Prognostic and predictive notes")
    out.append(integrated.get("prognostic_predictive_notes", "") or "_(none)_")
    out.append("")
    out.append("## 11. Limitations / pending studies")
    out.append(integrated.get("limitations_pending", "") or "_(none)_")
    out.append("")

    if show_evidence:
        out.append("---")
        out.append("**Part B — Evidence Trace (sections 8 and 9)**")
        out.append("")
        out.append(_evidence_trace_md(trace))
        out.append("")

    if show_qa:
        out.append("---")
        out.append("## QA Flags")
        out.append("")
        out.append(_flags_md(flags))

    return "\n".join(out)


def _narrative(d: dict[str, Any]) -> str:
    integrated = d.get("integrated_report", {}) or {}
    parts = []
    parts.append(integrated.get("clinical_context", "").strip())
    dx_lines = integrated.get("final_integrated_diagnosis", []) or []
    if dx_lines:
        parts.append("Final integrated diagnosis: " + " ".join(dx_lines))
    interp = integrated.get("integrated_interpretation", []) or []
    if interp:
        parts.append(" ".join(interp))
    pnotes = integrated.get("prognostic_predictive_notes", "")
    if pnotes:
        parts.append("Prognostic / predictive notes: " + pnotes)
    return "\n\n".join(p for p in parts if p)


def _json(d: dict[str, Any]) -> str:
    return json.dumps({
        "case_id": d.get("case_id"),
        "tumor_family": d.get("tumor_family"),
        "integrated_report": d.get("integrated_report", {}),
        "evidence_trace": d.get("evidence_trace", []),
        "qa_flags": d.get("flags", []),
    }, indent=2, default=str)


def _html(d: dict[str, Any]) -> str:
    integrated = d.get("integrated_report", {}) or {}
    trace = d.get("evidence_trace", []) or []
    flags = d.get("flags", []) or []
    run_config = d.get("run_config", {}) or {}
    show_evidence = run_config.get("show_evidence", True)
    show_qa = run_config.get("show_qa", True)

    body = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Integrated Diagnostic Report</title>",
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1080px;margin:24px auto;"
        "padding:0 16px;color:#111}"
        "h1{margin-bottom:0;color:#1a1a1a}h2{color:#444;margin-top:24px}"
        ".meta{color:#666;font-size:13px;margin-top:4px}"
        ".section{margin-top:16px}"
        ".dx li{font-weight:bold}"
        "table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}"
        "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}"
        "th{background:#f4f4f4}"
        ".flag-low{background:#fffbe6}.flag-medium{background:#ffe9d1}"
        ".flag-high{background:#ffd5d1}"
        ".flag{padding:6px 12px;margin:4px 0;border-left:4px solid #999}"
        "</style></head><body>",
        f"<h1>Integrated Diagnostic Report</h1>",
        f"<p class='meta'>Case: <b>{d.get('case_id','')}</b> · "
        f"Tumor family: <b>{d.get('tumor_family','')}</b></p>",
        "<h2>1. Patient and specimen identification</h2>",
        f"<p>{integrated.get('patient_specimen_id', '') or '<i>(not provided)</i>'}</p>",
        "<h2>2. Component studies reviewed</h2>",
        "<table><tr><th>Source</th><th>Lab</th><th>Accession</th><th>Reported</th></tr>",
    ]
    for s in integrated.get("component_studies", []) or []:
        body.append(
            f"<tr><td>{s.get('source_id','')}</td><td>{s.get('lab','')}</td>"
            f"<td>{s.get('accession','')}</td><td>{s.get('report_date','')}</td></tr>"
        )
    body.append("</table>")
    for n, title, key in [
        (3, "Clinical context", "clinical_context"),
        (4, "Morphology summary", "morphology_summary"),
        (5, "Flow / IHC summary", "flow_or_ihc_summary"),
        (6, "Cytogenetics summary", "cytogenetics_summary"),
        (7, "Molecular summary", "molecular_summary"),
    ]:
        body.append(f"<h2>{n}. {title}</h2>")
        body.append(f"<p>{integrated.get(key, '') or '<i>(not applicable)</i>'}</p>")
    body.append("<h2>8. Integrated interpretation</h2>")
    body.append("<ol>")
    for s in integrated.get("integrated_interpretation", []) or []:
        body.append(f"<li>{s}</li>")
    body.append("</ol>")
    body.append("<h2>9. Final integrated diagnosis</h2>")
    body.append("<ol class='dx'>")
    for s in integrated.get("final_integrated_diagnosis", []) or []:
        body.append(f"<li>{s}</li>")
    body.append("</ol>")
    body.append("<h2>10. Prognostic and predictive notes</h2>")
    body.append(f"<p>{integrated.get('prognostic_predictive_notes', '') or '<i>(none)</i>'}</p>")
    body.append("<h2>11. Limitations / pending studies</h2>")
    body.append(f"<p>{integrated.get('limitations_pending', '') or '<i>(none)</i>'}</p>")

    if show_evidence:
        body.append("<h2>Part B — Evidence Trace</h2>")
        body.append("<table><tr><th>#</th><th>Section</th><th>Sentence</th>"
                    "<th>Source(s)</th><th>Basis</th></tr>")
        for row in trace:
            srcs = ", ".join(row.get("supporting_source_ids", []) or [])
            body.append(
                f"<tr><td>{row.get('sentence_number','')}</td>"
                f"<td>{row.get('section','')}</td>"
                f"<td>{row.get('sentence','')}</td>"
                f"<td>{srcs}</td><td>{row.get('basis','')}</td></tr>"
            )
        body.append("</table>")

    if show_qa:
        body.append("<h2>QA Flags</h2>")
        if not flags:
            body.append("<p><i>No QA flags raised.</i></p>")
        else:
            for f in flags:
                sev = (f.get("severity", "low") or "low").lower()
                body.append(
                    f"<div class='flag flag-{sev}'><b>{sev.upper()}</b> "
                    f"[{f.get('category','')}] — {f.get('concern','')} "
                    f"<i>({f.get('reference','')})</i></div>"
                )

    body.append("</body></html>")
    return "\n".join(body)


class ScenarioD_v2_ReportFormatter(Component):
    display_name = "Report Formatter"
    description = (
        "Pure-Python renderer for Omar's 11-section integrated report + Part B "
        "evidence trace. Formats: integrated (markdown), narrative, json, html. "
        "Reads output_format / show_evidence / show_qa overrides from the chat "
        "directive when Pipeline Config is connected upstream."
    )
    icon = "file-text"
    name = "ReportFormatter S-D.V2"

    inputs = [
        HandleInput(
            name="reviewed",
            display_name="Reviewed",
            input_types=["Data"],
            info="Connect the QA Reviewer's output.",
        ),
        StrInput(
            name="format",
            display_name="Format",
            value="integrated",
            info="One of: integrated, narrative, json, html.",
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
        run_config = d.get("run_config", {}) or {}
        fmt = (run_config.get("output_format") or self.format or "integrated").strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(f"Format must be one of {sorted(VALID_FORMATS)}, got {fmt!r}")

        if fmt == "integrated":
            text = _integrated_md(d)
        elif fmt == "narrative":
            text = _narrative(d)
        elif fmt == "json":
            text = _json(d)
        else:
            text = _html(d)

        if self.header_note and fmt in {"integrated", "narrative"}:
            text = self.header_note.strip() + "\n\n" + text
        elif self.header_note and fmt == "html":
            text = text.replace("<body>", f"<body><p><em>{self.header_note}</em></p>")

        return Message(text=text)
