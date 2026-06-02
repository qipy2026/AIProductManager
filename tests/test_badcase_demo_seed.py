"""七层演示 Bad Case 种子数据测试."""

from backend.badcase.attribution_infer import infer_attribution_from_badcase
from backend.badcase.demo_samples import DEMO_BADCASES, DEMO_MARKER, seed_demo_badcases


def test_demo_samples_cover_seven_layers():
    attrs = {infer_attribution_from_badcase(s, force=True) for s in DEMO_BADCASES}
    assert attrs == {
        "skill",
        "prompt",
        "model",
        "knowledge",
        "retrieval",
        "flow",
        "memory",
    }
    assert len(DEMO_BADCASES) == 7


def test_seed_demo_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("OPS_DB", "sqlite")
    monkeypatch.setenv("AGENTOPS_DB", str(tmp_path / "demo.db"))

    from importlib import reload
    import backend.config as cfg
    import backend.db.sqlite_store as sqlite_store

    reload(cfg)
    reload(sqlite_store)

    result = seed_demo_badcases(sqlite_store)
    assert result["added"] == 7
    assert len(result["by_attribution"]) == 7

    items = sqlite_store.badcase_list(20)
    demo = [i for i in items if (i.get("note") or "").startswith(DEMO_MARKER)]
    assert len(demo) == 7

    result2 = seed_demo_badcases(sqlite_store)
    assert result2["deleted"] == 7
    assert result2["added"] == 7
