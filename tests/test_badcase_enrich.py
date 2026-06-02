"""Tests for Bad Case enrichment."""

from backend.badcase.enrich import enrich_badcase, enrich_badcase_list


def test_enrich_badcase_skill_layer():
    item = {
        "case_id": "TC-L1-001",
        "layer": "L1",
        "attribution": "eval_failure",
        "failures": ["must_invoke ticket-query: missing"],
        "note": "",
    }
    out = enrich_badcase(item)
    assert out["attribution"] == "skill"
    assert out["attribution_label"] == "Skill 层"
    assert out["fix_hint"]
    assert "must_invoke" in " ".join(out["failures"])


def test_enrich_badcase_list_counts():
    items = [
        {"layer": "L2", "attribution": "eval_failure", "failures": ["source refs"], "note": ""},
        {"layer": "L4", "attribution": "memory", "failures": [], "note": ""},
    ]
    out = enrich_badcase_list(items)
    assert out["total"] == 2
    assert out["by_attribution"].get("retrieval", 0) >= 1
    assert len(out["items"]) == 2
