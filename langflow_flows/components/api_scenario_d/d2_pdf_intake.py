"""Scenario D v2 — PDFIntake.

THIS is the document-AI step. It reads the pdfplumber raw-text dump of
the chosen fabricated report (a single linearized blob with repeating
page headers, broken tables, addenda appended, abbreviations without
expansion — exactly what a real extractor gets) and runs an LLM with
an editable system prompt to produce a structured `extracted` payload
in the shape the rest of the pipeline expects.

Optionally also runs a vision-capable model on the two embedded
placeholder images and folds those descriptions into the Data so the
Histology Synthesizer can use them.

There are TWO editable levers in this single component:
  - The extraction system prompt (this is the heart of the demo).
  - The vision system prompt (only used when use_vision=true).
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import (
    BoolInput,
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    make_image_message,
    openai_client,
    resolve_data_dir,
)


DEFAULT_EXTRACTION_PROMPT = """You are a document-AI extractor for
integrated pathology reports. The input is a raw text dump of a
multi-page PDF — produced by a generic PDF-text extractor — so it will
contain layout artifacts: page headers and footers repeated on every
page, tables flattened into space-separated rows, occasional column
collisions, character-encoding oddities (e.g. (cid:127), ‡, ligatures
like "fi"), and an ADDENDUM section appended after the primary
sign-out. Different labs format their reports differently — some are
prose-heavy with sections in ALL CAPS, others are table-heavy with
"TIER I/II/III" classifications, others use synoptic checklist
layouts. Your job is to ignore the noise and produce a clean
structured object.

Output a SINGLE JSON object with exactly these top-level fields. If a
field is genuinely absent from the report, use an empty string or
empty list — do NOT invent values.

{
  "tumor_family":       "glioma" | "medulloblastoma" | "breast" | "other",
  "demographics":       {"patient_id": "...", "age": <int|null>, "sex": "M"|"F"|"", "indication": "..."},
  "clinical_history":   "<full clinical-history paragraph>",
  "specimen":           "<specimen description>",
  "macroscopic":        "<gross description, may be empty>",
  "histology_text":     "<microscopic / histology description, full prose>",
  "ihc_profile":        [{"marker": "...", "result": "..."}, ...],
  "molecular_findings": {
    "snv_indel":         [{"gene": "...", "hgvsc": "...", "hgvsp": "...",
                            "vaf": <float|null>, "classification": "..."}],
    "structural_variants": [{"kind": "...", "description": "..."}],
    "copy_number":       [{"gene": "...", "copy_number": <int>, "kind": "..."}],
    "msi_status":        "<MSS|MSI-H|... or empty>",
    "tmb_mutations_per_mb": <float|null>,
    "methylation":       [{"locus": "...", "status": "..."}],
    "germline":          "<germline screen summary or empty>"
  },
  "pathologist_comments": "<the interpretation / comment paragraph(s)>",
  "addendum_text":        "<addendum body if one exists, else empty string>"
}

Rules:
  1. tumor_family must be inferred from the diagnosis / specimen /
     molecular findings — do not leave it empty unless truly unclear.
  2. Sweep across all pages — fields you need may appear after table
     breaks or in the ADDENDUM section at the end.
  3. Strip repeating page headers/footers and "Page N" markers before
     attributing text to a field.
  4. For tables flattened into rows, recover the columns from context
     (e.g. for an SNV table the columns are usually Gene / HGVSc /
     HGVSp / VAF / Classification).
  5. Preserve exact gene symbols and HGVS strings — do not paraphrase.
  6. Return ONLY the JSON object; no commentary, no markdown fences,
     no backticks. Use the word json in your reasoning if needed.
"""


DEFAULT_VISION_PROMPT = """You are a pathology image describer. For each
image you receive, write ONE concise paragraph (about 3 sentences)
describing the dominant features a pathologist would note: cellularity,
nuclear morphology, staining pattern, and whether the image is H&E or
immunohistochemical. Do NOT attempt diagnosis. Be specific about color
distribution. If an image clearly does not contain biological tissue,
say so plainly."""


_DEFAULT_IMAGES = {
    "sample_1": [
        {"label": "H&E ×20 — frontal lobe infiltrative astrocytic tumor", "kind": "he",
         "file": "images/sample_1_image_1.png"},
        {"label": "IDH1 R132H IHC ×20", "kind": "ihc",
         "file": "images/sample_1_image_2.png"},
    ],
    "sample_2": [
        {"label": "H&E ×20 — small round blue cell tumor", "kind": "he",
         "file": "images/sample_2_image_1.png"},
        {"label": "GAB1 IHC ×20 — cytoplasmic positivity", "kind": "ihc",
         "file": "images/sample_2_image_2.png"},
    ],
    "sample_3": [
        {"label": "H&E ×20 — invasive ductal carcinoma NST", "kind": "he",
         "file": "images/sample_3_image_1.png"},
        {"label": "ER IHC ×20 — Allred 8/8", "kind": "ihc",
         "file": "images/sample_3_image_2.png"},
    ],
}


def _fallback_extracted(sample_id: str) -> dict:
    """Minimal shape used when LLM extraction fails so downstream nodes
    don't blow up. Records a flag so the QA reviewer can see it."""
    return {
        "tumor_family": "",
        "demographics": {},
        "clinical_history": "",
        "specimen": "",
        "macroscopic": "",
        "histology_text": "",
        "ihc_profile": [],
        "molecular_findings": {
            "snv_indel": [], "structural_variants": [], "copy_number": [],
            "msi_status": "", "tmb_mutations_per_mb": None,
            "methylation": [], "germline": "",
        },
        "pathologist_comments": "",
        "addendum_text": "",
        "_extraction_failed": True,
    }


class ScenarioD_v2_PDFIntake(Component):
    display_name = "PDF Intake"
    description = (
        "Reads the raw-text dump of the chosen sample's PDF and uses an LLM to "
        "extract a structured payload. THIS is the document-AI step — the "
        "extraction system prompt is the workshop's key editable lever."
    )
    icon = "file-text"
    name = "PDFIntake S-D.V2"

    inputs = [
        HandleInput(
            name="run_config",
            display_name="Run Config",
            input_types=["Data"],
            required=False,
            info="Optional. Connect Pipeline Config to override Sample ID / use_vision from the chat directive.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(
            name="sample_id",
            display_name="Sample ID",
            value="sample_1",
            info="One of sample_1 (glioma), sample_2 (medulloblastoma), sample_3 (breast).",
        ),
        BoolInput(
            name="use_vision",
            display_name="Run Vision Call On Embedded Images",
            value=False,
            info="When true, a multimodal call describes the H&E/IHC placeholders.",
        ),
        StrInput(name="model", display_name="Extraction Model", value="openai/gpt-4o-mini",
                 info="The LLM that turns the raw PDF text into structured fields."),
        StrInput(name="vision_model", display_name="Vision Model", value="openai/gpt-4o",
                 info="Multimodal model used when Use Vision is on."),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens (extraction)", value=2500, advanced=True),
        IntInput(name="vision_max_tokens", display_name="Max Tokens (vision)", value=600, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="Extraction System Prompt",
            value=DEFAULT_EXTRACTION_PROMPT,
            info="EDIT ME. Reshape what the document-AI extractor pulls out of the raw text.",
        ),
        MultilineInput(
            name="vision_system_prompt",
            display_name="Vision System Prompt",
            value=DEFAULT_VISION_PROMPT,
            info="EDIT ME. Reshape how the vision model describes embedded images.",
        ),
    ]

    outputs = [Output(display_name="Intake", name="intake", method="run_intake")]

    def run_intake(self) -> Data:
        from tools.scenario_d import pdf_io

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        sample_id = run_config.get("sample_id", self.sample_id)
        use_vision = run_config.get("use_vision", self.use_vision)

        base = resolve_data_dir(self.data_dir)
        raw_text = pdf_io.load_raw_text(base, sample_id)

        client = openai_client()
        try:
            raw_llm = chat_completion_text(
                client,
                model=self.model,
                system_prompt=self.system_prompt or DEFAULT_EXTRACTION_PROMPT,
                user_content=raw_text,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                json_mode=True,
                span_name="scenario_d.pdf_intake.extraction",
            )
            extracted = json.loads(raw_llm)
            if not isinstance(extracted, dict):
                raise ValueError("extraction did not return a JSON object")
        except Exception as e:
            extracted = _fallback_extracted(sample_id)
            extracted["_extraction_error"] = f"{type(e).__name__}: {e}"
            raw_llm = ""

        # Backstop tumor_family for the WHO classifier downstream:
        # if the LLM failed to infer it from a messy dump, fall back to
        # a hint based on the sample_id chosen in the chat directive.
        if not extracted.get("tumor_family"):
            extracted["tumor_family"] = {
                "sample_1": "glioma",
                "sample_2": "medulloblastoma",
                "sample_3": "breast",
            }.get(sample_id, "")

        # Optional vision pass: embeds the two placeholder images for the
        # sample. Image filenames are deterministic per sample.
        image_descriptions: list[dict] = []
        if use_vision:
            images_meta = _DEFAULT_IMAGES.get(sample_id, [])
            if images_meta:
                images_payload = []
                try:
                    images_payload = [
                        (m["label"], pdf_io.load_image_bytes(base, m["file"]))
                        for m in images_meta
                    ]
                except FileNotFoundError as e:
                    image_descriptions.append({"label": "", "kind": "",
                                               "description": f"(image file missing: {e})"})

                if images_payload:
                    user_content = make_image_message(
                        text=(
                            "Describe each of the following images in one short "
                            "paragraph each. Number your paragraphs to match the "
                            "image order."
                        ),
                        images=images_payload,
                    )
                    try:
                        vision_raw = chat_completion_text(
                            client,
                            model=self.vision_model,
                            system_prompt=self.vision_system_prompt or DEFAULT_VISION_PROMPT,
                            user_content=user_content,
                            temperature=self.temperature,
                            max_tokens=self.vision_max_tokens,
                            span_name="scenario_d.pdf_intake.vision",
                        )
                        paragraphs = [p.strip() for p in vision_raw.split("\n\n") if p.strip()]
                        while len(paragraphs) < len(images_meta):
                            paragraphs.append("")
                        paragraphs = paragraphs[: len(images_meta)]
                        for m, desc in zip(images_meta, paragraphs):
                            image_descriptions.append({
                                "label": m["label"], "kind": m["kind"],
                                "description": desc,
                            })
                    except Exception as e:
                        for m in images_meta:
                            image_descriptions.append({
                                "label": m["label"], "kind": m["kind"],
                                "description": f"(vision call failed: {type(e).__name__})",
                            })

        return Data(data={
            "sample_id": sample_id,
            "tumor_family": extracted.get("tumor_family", ""),
            "extracted": extracted,
            "image_descriptions": image_descriptions,
            "extraction_raw_llm": raw_llm,
            "run_config": run_config,
        })
