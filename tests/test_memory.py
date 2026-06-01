"""Memory 体系测试 — UT-M-001~008."""

from datetime import datetime, timedelta, timezone

import pytest

from memory.router.router import MemoryRouter
from memory.stores.episodic import EpisodicMemoryStore, EpisodicRecord, redact_pii
from memory.stores.profile import ProfileMemoryStore
from memory.stores.working import WorkingMemoryStore


@pytest.fixture
def working() -> WorkingMemoryStore:
    s = WorkingMemoryStore()
    yield s
    s.clear()


@pytest.fixture
def episodic() -> EpisodicMemoryStore:
    s = EpisodicMemoryStore()
    yield s
    s.clear()


def test_ut_m_001_working_summarize_after_8_rounds(working: WorkingMemoryStore):
    wm = working.get("s1")
    for i in range(10):
        wm.append("user" if i % 2 == 0 else "assistant", f"msg-{i}")
    assert wm.summary != ""


def test_ut_m_002_working_recent_context(working: WorkingMemoryStore):
    wm = working.get("s2")
    wm.append("user", "那个订单 T-100 有问题")
    ctx = wm.to_context()
    assert len(ctx["recent_messages"]) >= 1
    assert "T-100" in ctx["recent_messages"][-1]["content"]


def test_ut_m_003_episodic_write_redacts_pii(episodic: EpisodicMemoryStore):
    episodic.write("u1", "用户手机13800138000报修")
    rec = episodic.read("u1")
    assert "[REDACTED]" in rec[0]["summary"]
    assert "13800138000" not in rec[0]["summary"]


def test_ut_m_004_episodic_expires_after_90_days(episodic: EpisodicMemoryStore):
    old = EpisodicRecord(
        user_id="u2",
        summary="old",
        created_at=datetime.now(timezone.utc) - timedelta(days=91),
    )
    episodic._records["u2"] = [old]
    assert episodic.read("u2") == []


def test_ut_m_005_profile_vip(profile_store=None):
    store = ProfileMemoryStore()
    p = store.get("user_vip")
    assert p is not None
    assert p.tier == "VIP"


def test_ut_m_006_refund_injects_episodic_and_profile():
    router = MemoryRouter()
    episodic = router.episodic
    episodic.write("u3", "历史退款咨询", ticket_ids=["T-010"])
    ctx, layers = router.inject(
        session_id="s",
        user_id="u3",
        message="我要退款",
        memory_deps=["working", "profile", "episodic"],
        intent="refund",
    )
    assert "profile" in layers
    assert "episodic" in layers


def test_ut_m_007_consult_skips_episodic():
    router = MemoryRouter()
    router.episodic.write("u4", "历史工单", ticket_ids=["T-001"])
    _, layers = router.inject(
        session_id="s",
        user_id="u4",
        message="企业版套餐",
        memory_deps=["working", "semantic"],
        intent="consult",
    )
    assert "episodic" not in layers
    assert "semantic" in layers


def test_ut_m_008_profile_wins_conflict():
    router = MemoryRouter()
    merged = router.resolve_conflict(
        {"tier": "VIP", "plan": "企业版"},
        {"tier": "standard", "plan": "专业版"},
    )
    assert merged["tier"] == "VIP"
    assert merged["plan"] == "企业版"


def test_redact_pii():
    assert redact_pii("call 13800138000") == "call [REDACTED]"
