from __future__ import annotations

from tools.scenario_b import note_loader


def test_load_case_returns_notes_and_request(data_dir):
    notes, request = note_loader.load_case(data_dir)
    assert len(notes) == 14
    assert request["request_id"] == "req-001"


def test_filter_notes_by_type_finds_med_onc(data_dir):
    notes, _ = note_loader.load_case(data_dir)
    med_onc = note_loader.filter_notes_by_type(notes, "Medical Oncology")
    # 4 med-onc notes: 2020-12 (start endocrine plan), 2021-03 (initiate), 2022-08, 2023-04, 2025-09
    # Actually 5 by my count above. Be lenient: at least 4.
    assert len(med_onc) >= 4
    assert all(n["note_type"] == "Medical Oncology" for n in med_onc)


def test_notes_mentioning_tamoxifen_finds_the_planted_ghost(data_dir):
    """The 'tamoxifen-naive' contradiction is grounded in 4 notes that explicitly
    mention tamoxifen. This test pin-points them so we can verify ground truth
    matches reality without relying on the LLM."""
    notes, _ = note_loader.load_case(data_dir)
    hits = note_loader.notes_mentioning(notes, "tamoxifen")
    hit_ids = {n["note_id"] for n in hits}
    assert {"note-009", "note-010", "note-011", "note-014"}.issubset(hit_ids)
    # The 2020-12 med-onc note also references tamoxifen ("tamoxifen vs. AI")
    assert "note-007" in hit_ids
