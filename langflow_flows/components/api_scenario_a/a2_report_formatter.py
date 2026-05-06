"""Scenario A v2 — ReportFormatter.

Pure-Python renderer. Six output formats including the GA4GH Phenopacket
JSON (the workshop's clinical-grade structured output). Reads `format`
override from upstream run_config so the chat-input directive ("show as
phenopacket") rewires the output without touching the node.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from langflow.custom import Component
from langflow.io import HandleInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_a import phenopacket_emitter


VALID_FORMATS = {"markdown", "csv", "json", "phenopacket", "narrative", "html"}


def _row_for(rank_entry: dict[str, Any], variant: dict[str, Any], flag: dict[str, Any] | None) -> dict[str, Any]:
    cv = variant.get("clinvar") or {}
    g = variant.get("gnomad") or {}
    pm = variant.get("pubmed") or {}
    return {
        "rank": rank_entry.get("rank", ""),
        "variant_id": variant["id"],
        "gene": variant["gene"],
        "hgvsp": variant.get("hgvsp") or "",
        "hgvsc": variant.get("hgvsc") or "",
        "clinvar": cv.get("clinical_significance") or "",
        "af_global": g.get("af_global") if g.get("af_global") is not None else "",
        "pmids": ";".join(pm.get("pmids", [])) if pm else "",
        "rationale": rank_entry.get("rationale", ""),
        "qa_severity": (flag or {}).get("severity", ""),
        "qa_concern": (flag or {}).get("concern", ""),
    }


def _md(rows: list[dict[str, Any]], advisory: str) -> str:
    out = ["# Variant tournament — top picks", ""]
    if advisory:
        out += ["## Clinical context", "", advisory, ""]
    out += ["## Ranked variants", ""]
    out += ["| Rank | Variant | Gene | HGVS.p | ClinVar | AF | PMIDs | Rationale | QA |"]
    out += ["|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        af = f"{r['af_global']:.4g}" if isinstance(r['af_global'], float) else r['af_global']
        qa = f"{r['qa_severity']}: {r['qa_concern']}" if r['qa_severity'] else ""
        out.append(
            f"| {r['rank']} | {r['variant_id']} | {r['gene']} | {r['hgvsp']} | "
            f"{r['clinvar']} | {af} | {r['pmids']} | {r['rationale']} | {qa} |"
        )
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


def _json(rows: list[dict[str, Any]], advisory: str) -> str:
    return json.dumps({"clinical_context": advisory, "ranked": rows}, indent=2, default=str)


def _narrative(rows: list[dict[str, Any]], advisory: str) -> str:
    parts = []
    if advisory:
        parts.append(f"Clinical context: {advisory}\n")
    parts.append(f"This tournament returned {len(rows)} candidate(s).")
    for r in rows:
        flag = f" [QA-{r['qa_severity']}: {r['qa_concern']}]" if r['qa_severity'] else ""
        parts.append(
            f"\nRank {r['rank']} — {r['gene']} {r['hgvsp'] or r['hgvsc']} "
            f"({r['variant_id']}, ClinVar {r['clinvar'] or 'unscored'}, AF {r['af_global']}). "
            f"{r['rationale']}{flag}"
        )
    return "".join(parts)


def _phenopacket(top_variants: list[dict[str, Any]], rank_entries: list[dict[str, Any]], phenotype: dict[str, Any]) -> str:
    rationales = {r["variant_id"]: r.get("rationale", "") for r in rank_entries}
    pkt = phenopacket_emitter.emit(
        patient=phenotype,
        ranked_variants=top_variants,
        rationales=rationales,
    )
    return json.dumps(pkt, indent=2, default=str)


def _html(rows: list[dict[str, Any]], advisory: str) -> str:
    body = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Variant tournament — top picks</title>",
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1080px;margin:24px auto;padding:0 16px;color:#111}"
        "h1{margin-bottom:4px}h2{color:#444;margin-top:24px}"
        "table{border-collapse:collapse;width:100%;font-size:13px}"
        "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}"
        "th{background:#f4f4f4}"
        ".flag-low{background:#fffbe6}.flag-medium{background:#ffe9d1}.flag-high{background:#ffd5d1}"
        "</style></head><body>",
        "<h1>Variant tournament — top picks</h1>",
    ]
    if advisory:
        body.append("<h2>Clinical context</h2>")
        body.append(f"<p>{advisory}</p>")
    body.append("<h2>Ranked variants</h2>")
    body.append("<table><tr>"
                "<th>Rank</th><th>Variant</th><th>Gene</th><th>HGVS.p</th>"
                "<th>ClinVar</th><th>AF</th><th>PMIDs</th><th>Rationale</th><th>QA</th></tr>")
    for r in rows:
        sev = r['qa_severity']
        cls = f" class='flag-{sev}'" if sev else ""
        qa = f"{sev}: {r['qa_concern']}" if sev else ""
        af = f"{r['af_global']:.4g}" if isinstance(r['af_global'], float) else r['af_global']
        body.append(
            f"<tr{cls}><td>{r['rank']}</td><td>{r['variant_id']}</td>"
            f"<td>{r['gene']}</td><td>{r['hgvsp']}</td><td>{r['clinvar']}</td>"
            f"<td>{af}</td><td>{r['pmids']}</td><td>{r['rationale']}</td><td>{qa}</td></tr>"
        )
    body.append("</table></body></html>")
    return "\n".join(body)


class ScenarioA_v2_ReportFormatter(Component):
    display_name = "Report Formatter"
    description = (
        "Pure-Python renderer. Outputs markdown / csv / json / phenopacket / narrative / html. "
        "Picks up `format` override from the chat-input directive when connected upstream."
    )
    icon = "file-text"
    name = "ReportFormatter S-A.V2"

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
            info="One of: markdown, csv, json, phenopacket, narrative, html.",
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
        candidates = d.get("cases", [])
        ranked = d.get("ranked", [])
        flags = d.get("flags", [])
        advisory = d.get("clinical_context", "")
        phenotype = d.get("phenotype", {})
        run_config = d.get("run_config", {})

        # Build rows ordered by rank entry, joining variant + flag info.
        cand_by_id = {v["id"]: v for v in candidates}
        flag_by_id = {f["variant_id"]: f for f in flags}

        ranked_sorted = sorted(ranked, key=lambda r: r.get("rank", 99))
        rows = []
        ranked_variants = []
        for r in ranked_sorted:
            v = cand_by_id.get(r.get("variant_id"))
            if not v:
                continue
            rows.append(_row_for(r, v, flag_by_id.get(v["id"])))
            ranked_variants.append(v)

        fmt = (run_config.get("format") or self.format or "markdown").strip().lower()
        if fmt not in VALID_FORMATS:
            raise ValueError(f"Format must be one of {sorted(VALID_FORMATS)}, got {fmt!r}")

        if fmt == "markdown":
            text = _md(rows, advisory)
        elif fmt == "csv":
            text = _csv(rows)
        elif fmt == "json":
            text = _json(rows, advisory)
        elif fmt == "narrative":
            text = _narrative(rows, advisory)
        elif fmt == "html":
            text = _html(rows, advisory)
        elif fmt == "phenopacket":
            text = _phenopacket(ranked_variants, ranked_sorted, phenotype)

        if self.header_note and fmt in {"markdown", "narrative"}:
            text = self.header_note.strip() + "\n\n" + text
        elif self.header_note and fmt == "html":
            text = text.replace("<body>", f"<body><p><em>{self.header_note}</em></p>")

        return Message(text=text)
