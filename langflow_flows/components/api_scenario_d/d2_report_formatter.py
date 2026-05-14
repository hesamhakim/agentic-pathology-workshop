"""Scenario D v2 — ReportFormatter.

Pure-Python renderer. Four output formats. Reads format override from
upstream run_config so the chat-input directive ("output as html")
rewires output without touching the node.
"""

from __future__ import annotations

import json
from typing import Any

from langflow.custom import Component
from langflow.io import HandleInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message


VALID_FORMATS = {"who_layered", "narrative", "json", "html"}


def _layered_md(d: dict[str, Any]) -> str:
    c = d.get("classification", {})
    flags = d.get("flags", [])
    out = []
    extracted = d.get("extracted", {})
    demo = extracted.get("demographics", {})
    sample_id = d.get("sample_id", "")
    out.append(f"# Integrated Diagnostic Report — {sample_id}")
    out.append("")
    out.append(
        f"**Patient:** {demo.get('patient_id','?')} | "
        f"{demo.get('age','?')} {demo.get('sex','?')} | "
        f"{demo.get('indication','')}"
    )
    out.append(f"**Specimen:** {extracted.get('specimen','')}")
    out.append("")
    out.append("## Integrated diagnosis (WHO layered)")
    out.append("")
    out.append(f"- **Layer 1 — Integrated diagnosis:** {c.get('integrated_diagnosis','')}")
    out.append(f"- **Layer 2 — Histologic diagnosis:** {c.get('histologic_diagnosis','')}")
    grade = c.get("who_grade")
    out.append(f"- **Layer 3 — WHO grade:** {grade if grade is not None else 'n/a'}")
    mfeat = c.get("molecular_features", [])
    out.append(
        "- **Layer 4 — Molecular features:** "
        + (", ".join(mfeat) if mfeat else "none reported")
    )
    out.append("")
    out.append(f"**Guideline source:** {c.get('guideline_source','')}")
    out.append("")
    if c.get("rationale"):
        out.append("## Rationale")
        out.append("")
        out.append(c["rationale"])
        out.append("")
    if c.get("evidence"):
        out.append("## Evidence")
        out.append("")
        out.append("| Feature | Source |")
        out.append("|---|---|")
        for e in c["evidence"]:
            out.append(f"| {e.get('feature','')} | {e.get('source','')} |")
        out.append("")
    if flags:
        out.append("## QA flags")
        out.append("")
        for f in flags:
            out.append(f"- **{f.get('severity','low').upper()}** — {f.get('finding','')}: {f.get('concern','')}")
        out.append("")
    return "\n".join(out)


def _narrative(d: dict[str, Any]) -> str:
    c = d.get("classification", {})
    flags = d.get("flags", [])
    parts = []
    parts.append(f"Integrated diagnosis: {c.get('integrated_diagnosis','')}.")
    if c.get("rationale"):
        parts.append(c["rationale"])
    mfeat = c.get("molecular_features", [])
    if mfeat:
        parts.append("Key molecular features: " + ", ".join(mfeat) + ".")
    grade = c.get("who_grade")
    if grade is not None:
        parts.append(f"WHO grade: {grade}.")
    if c.get("guideline_source"):
        parts.append(f"Per {c['guideline_source']}.")
    if flags:
        parts.append(
            "QA notes: "
            + "; ".join(
                f"[{f.get('severity','low')}] {f.get('finding','')}: {f.get('concern','')}"
                for f in flags
            )
        )
    return " ".join(parts)


def _json(d: dict[str, Any]) -> str:
    extracted = d.get("extracted", {})
    return json.dumps({
        "sample_id": d.get("sample_id"),
        "tumor_family": d.get("tumor_family"),
        "patient": extracted.get("demographics", {}),
        "classification": d.get("classification", {}),
        "qa_flags": d.get("flags", []),
        "guideline_blue_book": d.get("guideline_blue_book", ""),
    }, indent=2, default=str)


def _html(d: dict[str, Any]) -> str:
    c = d.get("classification", {})
    extracted = d.get("extracted", {})
    demo = extracted.get("demographics", {})
    sample_id = d.get("sample_id", "")
    flags = d.get("flags", [])

    body = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>WHO Integrated Diagnosis</title>",
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#111}"
        "h1{margin-bottom:0;color:#1a1a1a}h2{color:#444;margin-top:24px}"
        ".meta{color:#666;font-size:13px;margin-top:4px}"
        ".layer{margin:6px 0;padding:6px 12px;border-left:4px solid #4a90e2;background:#f6fafd}"
        ".layer b{color:#1a1a1a}"
        ".flag-low{background:#fffbe6;border-left-color:#e0a700}"
        ".flag-medium{background:#ffe9d1;border-left-color:#d97000}"
        ".flag-high{background:#ffd5d1;border-left-color:#c0392b}"
        ".flag{padding:6px 12px;margin:4px 0;border-left:4px solid #999}"
        "table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}"
        "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left}"
        "th{background:#f4f4f4}"
        "</style></head><body>",
        f"<h1>Integrated Diagnostic Report</h1>",
        f"<p class='meta'>Sample: <b>{sample_id}</b> &middot; Patient {demo.get('patient_id','?')} "
        f"({demo.get('age','?')} {demo.get('sex','?')}) &middot; {demo.get('indication','')}</p>",
        f"<p class='meta'>Specimen: {extracted.get('specimen','')}</p>",
        "<h2>Integrated diagnosis (WHO layered)</h2>",
        f"<div class='layer'><b>Layer 1 — Integrated diagnosis:</b> {c.get('integrated_diagnosis','')}</div>",
        f"<div class='layer'><b>Layer 2 — Histologic diagnosis:</b> {c.get('histologic_diagnosis','')}</div>",
        f"<div class='layer'><b>Layer 3 — WHO grade:</b> "
        f"{c.get('who_grade') if c.get('who_grade') is not None else 'n/a'}</div>",
        "<div class='layer'><b>Layer 4 — Molecular features:</b> "
        + (", ".join(c.get("molecular_features", [])) or "none reported") + "</div>",
        f"<p class='meta'>Guideline source: {c.get('guideline_source','')}</p>",
    ]
    if c.get("rationale"):
        body.append("<h2>Rationale</h2>")
        body.append(f"<p>{c['rationale']}</p>")
    if c.get("evidence"):
        body.append("<h2>Evidence</h2><table><tr><th>Feature</th><th>Source</th></tr>")
        for e in c["evidence"]:
            body.append(f"<tr><td>{e.get('feature','')}</td><td>{e.get('source','')}</td></tr>")
        body.append("</table>")
    if flags:
        body.append("<h2>QA flags</h2>")
        for f in flags:
            sev = (f.get("severity") or "low").lower()
            body.append(
                f"<div class='flag flag-{sev}'><b>{sev.upper()}</b> — "
                f"{f.get('finding','')}: {f.get('concern','')}</div>"
            )
    body.append("</body></html>")
    return "\n".join(body)


class ScenarioD_v2_ReportFormatter(Component):
    display_name = "Report Formatter"
    description = (
        "Pure-Python renderer. Outputs WHO-layered Markdown, narrative paragraph, "
        "JSON, or HTML. Picks up `output_format` override from the chat directive "
        "when Pipeline Config is connected upstream."
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
            value="who_layered",
            info="One of: who_layered, narrative, json, html.",
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
        run_config = d.get("run_config", {})
        fmt = (run_config.get("output_format") or self.format or "who_layered").strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(f"Format must be one of {sorted(VALID_FORMATS)}, got {fmt!r}")

        if fmt == "who_layered":
            text = _layered_md(d)
        elif fmt == "narrative":
            text = _narrative(d)
        elif fmt == "json":
            text = _json(d)
        else:
            text = _html(d)

        if self.header_note and fmt in {"who_layered", "narrative"}:
            text = self.header_note.strip() + "\n\n" + text
        elif self.header_note and fmt == "html":
            text = text.replace("<body>", f"<body><p><em>{self.header_note}</em></p>")

        return Message(text=text)
