"""ROI API tests."""

from backend.ops.roi import build_roi_snapshot


def test_build_roi_snapshot_structure():
    out = build_roi_snapshot(trace_count=10, badcase_count=2, skills=[])
    assert "metrics" in out
    assert len(out["metrics"]) == 7
    assert out["eval"]["gate"] == 0.85
    assert "headline" in out


def test_roi_metrics_have_baseline_and_current():
    out = build_roi_snapshot(trace_count=100, badcase_count=0, skills=[])
    fcr = next(m for m in out["metrics"] if m["key"] == "first_contact_resolution")
    assert fcr["baseline"] == 45.0
    assert fcr["current"] > fcr["baseline"]
