"""Generate the five Marp slide diagrams under docs/slides/img/.

Run with the `general` mamba env (matplotlib + reportlab + PIL are
already there):

    /mnt/data/envs/general/bin/python scripts/build_slide_diagrams.py

All five SVGs are written deterministically from data already in the
repo: the AML case manifest, the Scenario D pipeline JSON, and the
planted features in case_aml's extracted_ground_truth.json. Re-running
this script is the single source of truth for the slide-deck artwork.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MplPath


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "slides" / "img"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# When --png is passed on the command line, write PNG copies alongside
# the SVGs for visual review. Cheap to do (matplotlib supports both
# formats from the same figure) and avoids depending on any external
# svg→png renderer.
_WRITE_PNG = "--png" in __import__("sys").argv


# Consistent palette across all diagrams
NAVY     = "#1f3864"   # primary blue: agentic / structured / authoritative
NAVY_LT  = "#dde4ef"   # very light blue fill
AMBER    = "#b06f00"   # accent: agentic edge / "new"
AMBER_LT = "#fff4e0"
GRAY     = "#666666"   # deterministic / supporting
GRAY_LT  = "#eeeeee"
RED      = "#9b1a1a"   # failure / lane-discipline / "no trace"
RED_LT   = "#fde6e6"
GREEN    = "#1f6b1f"   # success / classifying / has-trace
GREEN_LT = "#e3f1e3"
TEXT     = "#1a1a1a"
FAINT    = "#9a9a9a"


def _new_figure(width=12, height=6.75):
    """16:9 aspect ratio, slide-sized canvas."""
    fig, ax = plt.subplots(figsize=(width, height), dpi=120)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def _box(ax, x, y, w, h, *, label=None, sublabel=None, fill=NAVY_LT, edge=NAVY,
        lw=1.5, label_color=NAVY, label_size=11, sub_color=TEXT, sub_size=8,
        rounding=0.04, label_bold=True, title_top=False):
    """Draw a rounded box centered at (x, y) with width w and height h.

    If `title_top=True`, the label is positioned near the top of the box
    instead of centered — useful when the box also has body text drawn
    separately at the center."""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding * min(w, h)}",
        linewidth=lw, edgecolor=edge, facecolor=fill,
    )
    ax.add_patch(box)
    if label is None:
        return
    if title_top:
        label_y = y + h * 0.35
    elif sublabel is None:
        label_y = y
    else:
        label_y = y + h * 0.20
    ax.text(x, label_y, label, ha="center", va="center",
            fontsize=label_size,
            fontweight="bold" if label_bold else "normal",
            color=label_color)
    if sublabel:
        ax.text(x, y - h * 0.22, sublabel, ha="center", va="center",
                fontsize=sub_size, color=sub_color, style="italic")


def _arrow(ax, x1, y1, x2, y2, *, color=NAVY, lw=1.6, label=None,
          label_color=None, style="->", curve=0.0):
    """Clean arrow via ax.annotate — gives proper arrowhead geometry."""
    arrowprops = dict(
        arrowstyle=style,
        color=color,
        linewidth=lw,
        shrinkA=0, shrinkB=0,
    )
    if curve:
        arrowprops["connectionstyle"] = f"arc3,rad={curve}"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arrowprops)
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + 0.12
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=7.5, color=label_color or color, style="italic")


def _save(fig, name: str) -> None:
    """Save a figure as SVG (canonical) and optionally PNG for review."""
    svg_path = OUT_DIR / f"{name}.svg"
    fig.savefig(svg_path, bbox_inches="tight", pad_inches=0.2)
    print("wrote", svg_path)
    if _WRITE_PNG:
        png_path = OUT_DIR / "_preview" / f"{name}.png"
        png_path.parent.mkdir(exist_ok=True)
        fig.savefig(png_path, bbox_inches="tight", pad_inches=0.2, dpi=140)
        print("wrote", png_path)
    plt.close(fig)


def _title(ax, x, y, text, *, size=18, color=TEXT, weight="bold"):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=size, color=color, fontweight=weight)


def _subtitle(ax, x, y, text, *, size=11, color=GRAY):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=size, color=color, style="italic")


def _bullet(ax, x, y, text, *, color=TEXT, size=10, marker="•", marker_color=None):
    ax.text(x, y, f"{marker}  {text}", ha="left", va="center",
            fontsize=size, color=color)


# =========================================================================
# Diagram 1 — Two ways to use an LLM
# =========================================================================

def diagram_concept_chatbot_vs_agent():
    fig, ax = _new_figure()

    _title(ax, 6, 6.35, "Two ways to use an LLM", size=20)

    # Vertical divider between panels
    ax.plot([6, 6], [0.4, 5.6], color=FAINT, lw=0.8, linestyle="--")

    # ---- LEFT: single LLM call ----
    _title(ax, 3, 5.6, "Single LLM call", size=14, color=NAVY)
    _subtitle(ax, 3, 5.25, "ChatGPT / Gemini / Claude / etc.", size=9)

    _box(ax, 3, 4.3, 1.6, 0.7, label="prompt", fill=GRAY_LT, edge=GRAY,
         label_color=GRAY, label_size=10, label_bold=False)
    _arrow(ax, 3, 3.93, 3, 3.45, color=GRAY)
    _box(ax, 3, 3, 2.4, 1.1, label="LLM", sublabel="one call",
         fill=NAVY_LT, edge=NAVY, label_color=NAVY, label_size=14)
    _arrow(ax, 3, 2.4, 3, 1.95, color=GRAY)
    _box(ax, 3, 1.55, 1.6, 0.7, label="answer", fill=GRAY_LT, edge=GRAY,
         label_color=GRAY, label_size=10, label_bold=False)

    # Annotations under the single-call panel
    _bullet(ax, 0.4, 0.95, "no per-claim trace",          color=RED, size=9.5, marker_color=RED)
    _bullet(ax, 0.4, 0.65, "structure varies run-to-run", color=RED, size=9.5, marker_color=RED)
    _bullet(ax, 3.0, 0.95, "no enforced rules",           color=RED, size=9.5, marker_color=RED)
    _bullet(ax, 3.0, 0.65, "no QA pass",                  color=RED, size=9.5, marker_color=RED)

    # ---- RIGHT: agentic workflow ----
    _title(ax, 9, 5.6, "Agentic workflow", size=14, color=AMBER)
    _subtitle(ax, 9, 5.25, "directed graph of LLM + deterministic steps", size=9)

    # 5 nodes laid out: in → s1 → (a, b in parallel) → s2 → out
    _box(ax, 7.0, 4.3, 1.0, 0.55, label="in",       fill=GRAY_LT, edge=GRAY,
         label_color=GRAY, label_size=9, label_bold=False)
    _box(ax, 8.4, 4.3, 1.2, 0.55, label="extract",  fill=NAVY_LT,  edge=NAVY,
         label_color=NAVY,  label_size=9.5)
    _box(ax, 9.7, 4.9, 1.2, 0.55, label="branch A", fill=NAVY_LT,  edge=NAVY,
         label_color=NAVY,  label_size=9.5)
    _box(ax, 9.7, 3.7, 1.2, 0.55, label="branch B", fill=NAVY_LT,  edge=NAVY,
         label_color=NAVY,  label_size=9.5)
    _box(ax, 11.0, 4.3, 1.2, 0.55, label="integrate", fill=AMBER_LT, edge=AMBER,
         label_color=AMBER, label_size=9.5)
    # Output node — pushed off canvas a touch so the row stays clean; replace with stacked QA/sidebar instead
    _box(ax, 11.0, 3.0, 1.2, 0.55, label="QA / trace", fill=AMBER_LT, edge=AMBER,
         label_color=AMBER, label_size=9.5)
    _box(ax, 11.0, 1.85, 1.2, 0.55, label="report", fill=GRAY_LT, edge=GRAY,
         label_color=GRAY, label_size=9, label_bold=False)

    # Arrows
    _arrow(ax, 7.5, 4.3, 7.85, 4.3, color=NAVY)
    _arrow(ax, 8.95, 4.4, 9.2, 4.85, color=NAVY)
    _arrow(ax, 8.95, 4.2, 9.2, 3.75, color=NAVY)
    _arrow(ax, 10.25, 4.85, 10.5, 4.4, color=NAVY)
    _arrow(ax, 10.25, 3.75, 10.5, 4.2, color=NAVY)
    _arrow(ax, 11.0, 4.05, 11.0, 3.25, color=AMBER, lw=1.2)
    _arrow(ax, 11.0, 2.75, 11.0, 2.10, color=AMBER, lw=1.2)

    # Annotations under the agentic panel
    _bullet(ax, 6.4, 0.95, "every claim traces to a source", color=GREEN, size=9.5)
    _bullet(ax, 6.4, 0.65, "structured output for downstream",  color=GREEN, size=9.5)
    _bullet(ax, 9.6, 0.95, "deterministic where possible",   color=GREEN, size=9.5)
    _bullet(ax, 9.6, 0.65, "QA flags any failure mode",      color=GREEN, size=9.5)

    _save(fig, "concept_chatbot_vs_agent")


# =========================================================================
# Diagram 2 — One patient, four reports
# =========================================================================

def diagram_case_aml_overview():
    fig, ax = _new_figure()

    _title(ax, 6, 6.35, "One patient, four separately-issued reports", size=18)
    _subtitle(ax, 6, 5.95, "Same diagnostic episode. Different labs. Different days.", size=10)

    # Center: patient
    cx, cy = 6, 3.2
    patient = mpatches.Circle((cx, cy), 0.7, facecolor=NAVY_LT, edgecolor=NAVY, lw=2)
    ax.add_patch(patient)
    ax.text(cx, cy + 0.12, "ONE", ha="center", va="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.text(cx, cy - 0.18, "PATIENT", ha="center", va="center", fontsize=9, color=NAVY)

    # 4 PDFs around the perimeter
    pdfs = [
        # (label, sublabel, x, y, source_id)
        ("Bone marrow morphology",   "manual blast count, cytochem",         1.8, 5.0, "MORPH"),
        ("Flow cytometry",           "gated blast %, immunophenotype",       10.2, 5.0, "FLOW"),
        ("Cytogenetics + FISH",      "karyotype, AML rearrangement panel",    1.8, 1.4, "CYTO"),
        ("Molecular NGS (54-gene)",  "SNV/indel, FLT3-ITD, VAF",            10.2, 1.4, "MOLEC"),
    ]
    pdf_w, pdf_h = 3.2, 1.05
    for label, sub, x, y, _sid in pdfs:
        _box(ax, x, y, pdf_w, pdf_h, fill="white", edge=GRAY, lw=1.2)
        # Modality title — centered, near top
        ax.text(x, y + 0.18, label, ha="center", va="center",
                fontsize=11, color=TEXT, fontweight="bold")
        # Description — centered, near bottom
        ax.text(x, y - 0.20, sub, ha="center", va="center",
                fontsize=8.5, color=GRAY, style="italic")

    # Arrows from each PDF converging toward the patient
    for _, _, x, y, _ in pdfs:
        # offset arrow endpoints so they don't enter the circle
        dx, dy = cx - x, cy - y
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        start_x = x + ux * 1.0
        start_y = y + uy * 0.42
        end_x = cx - ux * 0.75
        end_y = cy - uy * 0.75
        _arrow(ax, start_x, start_y, end_x, end_y, color=GRAY, lw=1.2)

    # Gold-standard diagnosis underneath
    ax.text(6, 0.7, "Gold-standard integrated diagnosis:",
            ha="center", va="center", fontsize=10, color=GRAY)
    ax.text(6, 0.35, "Acute myeloid leukemia with mutated NPM1, with monocytic differentiation",
            ha="center", va="center", fontsize=11.5, color=NAVY, fontweight="bold")

    _save(fig, "case_aml_overview")


# =========================================================================
# Diagram 3 — Four planted pedagogical features
# =========================================================================

def diagram_case_aml_features():
    fig, ax = _new_figure()

    _title(ax, 6, 6.35, "Four things a model has to get right", size=18)
    _subtitle(ax, 6, 5.95, "Planted in the case on purpose. Each has a known correct handling.", size=10)

    # Four feature cards laid out as 2x2 grid
    features = [
        # (title, body, color, color_lt, x, y, kind_tag)
        ("Discordance",
         "Morphology says 18% blasts.\nFlow says 22%.\nThe model must reconcile —\nnot silently pick one number.",
         AMBER, AMBER_LT, 3, 4.4, "MORPH ↔ FLOW"),
        ("Hedge resolution",
         "Morphology hedges on lineage.\nFlow proves monocytic differentiation.\nThe model must credit flow with\nresolving the hedge.",
         AMBER, AMBER_LT, 9, 4.4, "MORPH ↔ FLOW"),
        ("Single-source classifying",
         "NPM1 + FLT3-ITD appear only\nin the molecular report.\nKaryotype and FISH are normal.\nThe whole diagnosis hinges here.",
         GREEN, GREEN_LT, 3, 1.85, "MOLEC only"),
        ("Lane discipline",
         "DNMT3A R882H is real and Tier II.\nBut it does NOT classify the disease.\nIt belongs in prognostic notes —\nNOT in the diagnosis line.",
         RED, RED_LT, 9, 1.85, "the trap"),
    ]
    for title, body, color, color_lt, x, y, tag in features:
        _box(ax, x, y, 4.8, 1.85, fill=color_lt, edge=color, lw=2)
        # Title — near top of card
        ax.text(x, y + 0.65, title, ha="center", va="center",
                fontsize=14, color=color, fontweight="bold")
        # Tag — small inline subtitle below the title, same color, italic
        ax.text(x, y + 0.35, tag, ha="center", va="center",
                fontsize=8.5, color=color, style="italic", fontweight="bold")
        # Body — centered in the lower portion of the card
        ax.text(x, y - 0.25, body, ha="center", va="center",
                fontsize=9.5, color=TEXT, linespacing=1.35)

    _save(fig, "case_aml_features")


# =========================================================================
# Diagram 4 — Scenario D pipeline architecture
# =========================================================================

def diagram_pipeline_d():
    fig, ax = _new_figure(width=16, height=7.5)

    _title(ax, 8, 7.1, "Scenario D — Integrated Report → WHO  (the agentic workflow)", size=16)
    _subtitle(ax, 8, 6.7, "Seven components. Two LLM stages (extract → integrate). Per-sentence evidence trace built in.", size=10)

    # Nodes (label, subtitle, x, y, fill, edge, color)
    # 7 functional nodes (Chat I/O excluded — they're trivial bookends)
    nodes = [
        ("Chat Input",       "user msg +\npaperclip",                      1.0,  4.0, GRAY_LT,  GRAY,  GRAY),
        ("Pipeline Config",  "parses chat directive\ninto run config",     3.0,  4.0, NAVY_LT,  NAVY,  NAVY),
        ("PDF Intake",       "Stage 1 — multi-PDF\nstructured extraction\n+ cross-report obs.\n+ classifying flags", 5.3,  4.0, NAVY_LT,  NAVY,  NAVY),
        ("Molecular Parser", "split classifying\nvs prognostic\n(pure-Python)",  7.9,  5.4, GRAY_LT,  GRAY,  GRAY),
        ("Histology Synth",  "morphology + IHC\nsynthesis paragraph",      7.9,  2.6, NAVY_LT,  NAVY,  NAVY),
        ("WHO Classifier",   "Stage 2 — integrator\n11-section report\n+ Part B trace",       10.5, 4.0, AMBER_LT, AMBER, AMBER),
        ("QA Reviewer",      "UNSUPPORTED,\nlane discipline,\nrequired findings", 12.7, 4.0, AMBER_LT, AMBER, AMBER),
        ("Report Formatter", "markdown / json\nhtml / narrative",          14.7, 4.0, GRAY_LT,  GRAY,  GRAY),
    ]

    node_w, node_h = 1.85, 1.7
    for label, sub, x, y, fill, edge, col in nodes:
        _box(ax, x, y, node_w, node_h, fill=fill, edge=edge, lw=1.5)
        # Title at top of box
        ax.text(x, y + 0.5, label, ha="center", va="center",
                fontsize=11, color=col, fontweight="bold")
        # Subtitle in middle/lower of box
        ax.text(x, y - 0.18, sub, ha="center", va="center",
                fontsize=8, color=TEXT, linespacing=1.3)

    # Edges (from-idx, to-idx, color, type-label)
    edges_def = [
        (0, 1, NAVY,  "Message"),
        (1, 2, NAVY,  "Data"),
        (2, 3, NAVY,  "Data"),
        (2, 4, NAVY,  "Data"),
        (3, 5, NAVY,  "Data"),
        (4, 5, NAVY,  "Message"),
        (5, 6, AMBER, "Data"),
        (6, 7, AMBER, "Data"),
    ]
    half_w = node_w / 2
    for fi, ti, color, label_t in edges_def:
        x1, y1 = nodes[fi][2], nodes[fi][3]
        x2, y2 = nodes[ti][2], nodes[ti][3]
        if abs(y2 - y1) < 0.1:
            # Horizontal edge
            _arrow(ax, x1 + half_w, y1, x2 - half_w, y2, color=color, lw=1.3, label=label_t)
        else:
            # Diagonal edge — offset the start/end so the arrow doesn't
            # disappear inside the box
            dy = 0.5 if y2 > y1 else -0.5
            _arrow(ax, x1 + half_w * 0.85, y1 + dy, x2 - half_w * 0.85, y2 - dy,
                   color=color, lw=1.3, label=label_t)

    # Output indicator
    _arrow(ax, 14.7 + half_w, 4.0, 15.85, 4.0, color=GRAY, lw=1.3)

    # Legend (centered, with comfortable spacing)
    leg_y = 0.7
    ax.text(8, leg_y + 0.45, "Legend", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=TEXT)
    legend_items = [
        (4.0, NAVY_LT,  NAVY,  "LLM call"),
        (7.5, AMBER_LT, AMBER, "main reasoner / QA"),
        (11.3, GRAY_LT, GRAY,  "deterministic / I/O"),
    ]
    for x, fill, edge, label in legend_items:
        _box(ax, x, leg_y, 0.4, 0.28, fill=fill, edge=edge, lw=1)
        ax.text(x + 0.3, leg_y, label, ha="left", va="center", fontsize=9.5, color=TEXT)

    _save(fig, "pipeline_d")


# =========================================================================
# Diagram 5 — Side by side
# =========================================================================

def diagram_side_by_side():
    fig, ax = _new_figure(width=16, height=9)

    _title(ax, 8, 8.5, "Same four PDFs in. Two very different outputs.", size=18)

    # Common output-card horizontal placement so both rows align
    OUT_X = 13.0
    OUT_W = 5.6

    # ---- Top row: Scenario 0 ----
    ax.text(0.4, 7.4, "Scenario 0  —  general chatbot", ha="left", va="center",
            fontsize=13, color=NAVY, fontweight="bold")

    # Input label on the left
    ax.text(0.7, 6.4, "4 AML PDFs", ha="center", va="center",
            fontsize=9.5, color=GRAY, style="italic")
    ax.text(0.7, 6.10, "(via paperclip)", ha="center", va="center",
            fontsize=8, color=FAINT)
    _arrow(ax, 1.4, 6.4, 2.0, 6.4, color=GRAY)

    # 3-node pipeline (tightly packed, leaves room for output on right)
    _box(ax, 2.7,  6.4, 1.2, 0.65, fill=GRAY_LT, edge=GRAY, lw=1.3)
    ax.text(2.7, 6.4, "Chat Input", ha="center", va="center", fontsize=9.5, color=GRAY)
    _arrow(ax, 3.35, 6.4, 3.95, 6.4, color=GRAY)
    _box(ax, 4.75, 6.4, 1.7, 0.65, fill=NAVY_LT, edge=NAVY, lw=1.3)
    ax.text(4.75, 6.4, "General Chatbot", ha="center", va="center",
            fontsize=10.5, color=NAVY, fontweight="bold")
    _arrow(ax, 5.65, 6.4, 6.25, 6.4, color=GRAY)
    _box(ax, 7.05, 6.4, 1.2, 0.65, fill=GRAY_LT, edge=GRAY, lw=1.3)
    ax.text(7.05, 6.4, "Chat Output", ha="center", va="center", fontsize=9.5, color=GRAY)
    _arrow(ax, 7.7, 6.4, OUT_X - OUT_W / 2 - 0.1, 6.4, color=GRAY)

    # Output card (Scenario 0)
    _box(ax, OUT_X, 6.4, OUT_W, 1.05, fill=RED_LT, edge=RED, lw=1.6)
    ax.text(OUT_X, 6.65, "one prose reply", ha="center", va="center",
            fontsize=12, color=RED, fontweight="bold")
    ax.text(OUT_X, 6.15, "no trace · no structure · no QA · varies run-to-run",
            ha="center", va="center", fontsize=9, color=RED, style="italic")

    # ---- Bottom row: Scenario D ----
    ax.text(0.4, 4.0, "Scenario D  —  agentic workflow", ha="left", va="center",
            fontsize=13, color=AMBER, fontweight="bold")

    # Input label on the left
    ax.text(0.7, 3.0, "4 AML PDFs", ha="center", va="center",
            fontsize=9.5, color=GRAY, style="italic")
    ax.text(0.7, 2.70, "(case ID, attached)", ha="center", va="center",
            fontsize=8, color=FAINT)
    _arrow(ax, 1.4, 3.0, 2.0, 3.0, color=GRAY)

    # 7-node pipeline (tightly packed: width 0.9 with gaps of ~0.95)
    nwidth = 0.9
    nx_start = 2.55
    spacing = 1.05
    nx = [nx_start + i * spacing for i in range(7)]
    nlabels = ["Chat In", "Cfg", "PDFIntake", "Mol+Hist", "WHO Cls.", "QA", "Format"]
    ncolors = [(GRAY_LT, GRAY), (NAVY_LT, NAVY), (NAVY_LT, NAVY), (NAVY_LT, NAVY),
               (AMBER_LT, AMBER), (AMBER_LT, AMBER), (GRAY_LT, GRAY)]
    for x, lab, (fill, edge) in zip(nx, nlabels, ncolors):
        col = edge
        _box(ax, x, 3.0, nwidth, 0.6, fill=fill, edge=edge, lw=1.3)
        ax.text(x, 3.0, lab, ha="center", va="center",
                fontsize=8, color=col, fontweight="bold")
    for i in range(len(nx) - 1):
        edge_color = NAVY if i < 4 else AMBER
        _arrow(ax, nx[i] + nwidth / 2 + 0.02, 3.0,
              nx[i + 1] - nwidth / 2 - 0.02, 3.0,
              color=edge_color, lw=1.1)
    # Final arrow into the output card
    _arrow(ax, nx[-1] + nwidth / 2 + 0.02, 3.0,
          OUT_X - OUT_W / 2 - 0.1, 3.0, color=GRAY, lw=1.1)

    # Output card (Scenario D)
    _box(ax, OUT_X, 3.0, OUT_W, 1.05, fill=GREEN_LT, edge=GREEN, lw=1.6)
    ax.text(OUT_X, 3.25, "structured report + Part B trace + QA flags",
            ha="center", va="center", fontsize=11.5, color=GREEN, fontweight="bold")
    ax.text(OUT_X, 2.75, "11-section JSON / markdown · auditable · reproducible",
            ha="center", va="center", fontsize=9, color=GREEN, style="italic")

    # ---- Bottom comparison table ----
    table_top = 1.4
    rows = [
        ("",                                "Scenario 0",       "Scenario D"),
        ("Per-sentence evidence trace",     "no",               "yes (Part B)"),
        ("Structured machine-readable out", "no",               "yes (JSON / 11 sections)"),
        ("Lane-discipline enforced",        "no",               "yes (QA flag)"),
        ("Run-to-run consistency",          "variable",         "deterministic where possible"),
    ]
    col_x = [1.0, 9.0, 12.5]
    col_color = [TEXT, NAVY, AMBER]
    row_h = 0.26
    for ri, row in enumerate(rows):
        y = table_top - ri * row_h
        weight = "bold" if ri == 0 else "normal"
        for ci, cell in enumerate(row):
            ax.text(col_x[ci], y, cell,
                    ha="left", va="center", fontsize=10,
                    fontweight=weight,
                    color=col_color[ci] if ri == 0 else TEXT)
        if ri == 0:
            ax.plot([0.8, 15.2], [y - 0.13, y - 0.13], color=GRAY, lw=0.5)

    _save(fig, "side_by_side")


# =========================================================================
# Driver
# =========================================================================

def main():
    diagram_concept_chatbot_vs_agent()
    diagram_case_aml_overview()
    diagram_case_aml_features()
    diagram_pipeline_d()
    diagram_side_by_side()
    print()
    print(f"all five SVGs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
