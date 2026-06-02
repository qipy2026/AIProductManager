"""Eval 报告 enrichment 测试."""

from harness.eval.report_enrich import enrich_report, infer_fix_hint


def test_enrich_report_adds_case_metadata():
    raw = {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "pass_rate": 0.5,
        "by_layer": {"L5": {"passed": 1, "failed": 1, "total": 2}},
        "results": [
            {"case_id": "TC-L5-001", "layer": "L5", "passed": True, "failures": []},
            {
                "case_id": "TC-L5-002",
                "layer": "L5",
                "passed": False,
                "failures": ["must_invoke missing: ticket-create"],
            },
        ],
    }
    out = enrich_report(raw, gate=0.85)
    assert out["gate_passed"] is False
    assert len(out["layer_summary"]) == 5
    failed = out["failed_cases"][0]
    assert failed["case_id"] == "TC-L5-002"
    assert failed["message"] == "服务器宕机"
    assert failed["description"]
    assert failed["attribution"] == "skill"
    assert "graph.yaml" in failed["fix_hint"]
    assert failed["assertions"]["skill"]["must_invoke"] == ["ticket-create"]


def test_get_case_detail():
    from harness.eval.report_enrich import get_case_detail

    d = get_case_detail("TC-L5-002")
    assert d is not None
    assert d["input"]["message"] == "服务器宕机"
    assert "ticket-create" in d["assertions"]["skill"]["must_invoke"]


def test_infer_fix_hint_memory():
    hint = infer_fix_hint(["must_inject missing: episodic"], layer="L4")
    assert "Memory" in hint
