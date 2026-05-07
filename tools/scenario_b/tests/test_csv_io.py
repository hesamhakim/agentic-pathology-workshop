from __future__ import annotations

from tools.scenario_b import csv_io


def test_read_notes_count_and_sort(notes_path):
    notes = csv_io.read_notes(notes_path)
    assert len(notes) == 14
    # Sorted ascending by date — first should be the 2020-03 PCP visit
    assert notes[0]["note_id"] == "note-001"
    assert notes[0]["date"] == "2020-03-14"
    assert notes[-1]["note_id"] == "note-014"


def test_read_request_single_row(request_path):
    r = csv_io.read_request(request_path)
    assert r["request_id"] == "req-001"
    assert "tamoxifen-naive" in (r["claimed_history"] or "").lower()


def test_read_ground_truth_split_evidence_ids(ground_truth_path):
    gt = csv_io.read_ground_truth(ground_truth_path)
    assert len(gt) == 3
    g_ghost = next(g for g in gt if g["contradiction_id"] == "ghost-001")
    assert g_ghost["severity"] == "high"
    assert "note-009" in g_ghost["evidence_note_ids"]
    assert "note-014" in g_ghost["evidence_note_ids"]
