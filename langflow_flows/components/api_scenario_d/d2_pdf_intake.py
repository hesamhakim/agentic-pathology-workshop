"""Scenario D v2 — PDFIntake.

Loads the pre-extracted JSON sidecar for the chosen fabricated report.
When `use_vision` is on, makes a single multimodal call to the chosen
vision model and asks for a one-paragraph description of each embedded
image (synthetic H&E and IHC placeholders).

The PDF itself is a viewable artifact for attendees; the workflow reads
from the JSON sidecar so we don't need pdfplumber inside the langflow
container. To replace the sidecar with live PDF parsing, swap
`pdf_io.load_extracted` for a function that runs pdfplumber + an LLM
section-classifier.
"""

from __future__ import annotations

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


DEFAULT_VISION_PROMPT = """You are a pathology image describer. For each
image you receive, write ONE concise paragraph (about 3 sentences)
describing the dominant features a pathologist would note: cellularity,
nuclear morphology, staining pattern, and whether the image is H&E or
immunohistochemical. Do NOT attempt diagnosis. Be specific about color
distribution. If an image clearly does not contain biological tissue,
say so plainly."""


class ScenarioD_v2_PDFIntake(Component):
    display_name = "PDF Intake"
    description = (
        "Loads the pre-extracted JSON for the chosen sample. Optionally runs a vision "
        "model on the embedded H&E / IHC images and folds those descriptions into the "
        "Data object passed downstream."
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
        StrInput(name="model", display_name="Vision Model", value="openai/gpt-4o"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=600, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="Vision System Prompt",
            value=DEFAULT_VISION_PROMPT,
            info="EDIT ME. Reshape how the vision model describes images.",
        ),
    ]

    outputs = [Output(display_name="Intake", name="intake", method="run_intake")]

    def run_intake(self) -> Data:
        from tools.scenario_d import pdf_io

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        sample_id = run_config.get("sample_id", self.sample_id)
        use_vision = run_config.get("use_vision", self.use_vision)

        base = resolve_data_dir(self.data_dir)
        extracted = pdf_io.load_extracted(base, sample_id)

        image_descriptions: list[dict] = []
        if use_vision and extracted.get("images"):
            client = openai_client()
            images_payload = [
                (img["label"], pdf_io.load_image_bytes(base, img["file"]))
                for img in extracted["images"]
            ]
            user_content = make_image_message(
                text=(
                    "Describe each of the following images in one short paragraph each. "
                    "Number your paragraphs to match the image order."
                ),
                images=images_payload,
            )
            try:
                raw = chat_completion_text(
                    client,
                    model=self.model,
                    system_prompt=self.system_prompt or DEFAULT_VISION_PROMPT,
                    user_content=user_content,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    span_name="scenario_d.pdf_intake.vision",
                )
                # Split into per-image paragraphs by blank-line or numbered prefix.
                paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
                # Pad / trim to match image count
                while len(paragraphs) < len(extracted["images"]):
                    paragraphs.append("")
                paragraphs = paragraphs[: len(extracted["images"])]
                for img, desc in zip(extracted["images"], paragraphs):
                    image_descriptions.append({
                        "label": img["label"],
                        "kind": img["kind"],
                        "description": desc,
                    })
            except Exception as e:  # vision failure shouldn't kill the run
                for img in extracted["images"]:
                    image_descriptions.append({
                        "label": img["label"],
                        "kind": img["kind"],
                        "description": f"(vision call failed: {type(e).__name__})",
                    })

        return Data(data={
            "sample_id": sample_id,
            "tumor_family": extracted["tumor_family"],
            "extracted": extracted,
            "image_descriptions": image_descriptions,
            "run_config": run_config,
        })
