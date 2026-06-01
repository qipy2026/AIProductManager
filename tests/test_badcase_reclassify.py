"""Bad Case 自动归类测试."""

from backend.badcase.attribution_infer import infer_attribution_from_badcase
from backend.db.conversations import clear_all
from harness.runtime.trace_store import clear_traces


def setup_function():
    clear_traces()
    clear_all()


def test_infer_l1_skill():
    assert (
        infer_attribution_from_badcase(
            {
                "attribution": "eval_failure",
                "layer": "L1",
                "failures": ["must_invoke missing: ticket-query"],
            }
        )
        == "skill"
    )


def test_infer_l2_retrieval():
    assert (
        infer_attribution_from_badcase(
            {
                "attribution": "eval_failure",
                "layer": "L2",
                "failures": ["source refs missing"],
            }
        )
        == "retrieval"
    )


def test_infer_l4_memory():
    assert (
        infer_attribution_from_badcase(
            {
                "attribution": "eval_failure",
                "layer": "L4",
                "failures": ["must_inject missing: episodic"],
            }
        )
        == "memory"
    )


def test_infer_blocked_flow():
    assert (
        infer_attribution_from_badcase(
            {
                "attribution": "eval_failure",
                "layer": "L5",
                "failures": ["expected blocked=true"],
            }
        )
        == "flow"
    )


def test_reclassify_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("OPS_DB", "sqlite")
    monkeypatch.setenv("AGENTOPS_DB", str(tmp_path / "bc.db"))

    from importlib import reload
    import backend.config as cfg
    import backend.db.sqlite_store as sqlite_store

    reload(cfg)
    reload(sqlite_store)

    sqlite_store.badcase_add(
        case_id="TC-L1-001",
        layer="L1",
        attribution="eval_failure",
        note="must_invoke missing: x",
        failures=["must_invoke missing: x"],
    )
    sqlite_store.badcase_add(
        case_id="TC-L2-001",
        layer="L2",
        attribution="eval_failure",
        failures=["source refs missing"],
    )
    result = sqlite_store.badcase_reclassify_all()
    assert result["total"] == 2
    assert result["updated"] == 2
    items = sqlite_store.badcase_list(10)
    attrs = {i["case_id"]: i["attribution"] for i in items}
    assert attrs["TC-L1-001"] == "skill"
    assert attrs["TC-L2-001"] == "retrieval"
