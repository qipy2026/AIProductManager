"""Orchestrator 测试 — UT-S-005~007."""

import pytest

from backend.tools.ticket_mock import ticket_api
from harness.runtime.context import HarnessContext
from memory.router.router import working_store
from skills.orchestrator.orchestrator import SkillOrchestrator


@pytest.fixture(autouse=True)
def _reset():
    ticket_api.clear()
    working_store.clear()
    yield
    ticket_api.clear()
    working_store.clear()


@pytest.fixture
def orch() -> SkillOrchestrator:
    return SkillOrchestrator()


def test_ut_s_005_consult_path_retrieve_compose(orch: SkillOrchestrator):
    ctx = HarnessContext(
        message="企业版和专业版有什么区别？",
        session_id="o1",
    )
    ctx = orch.run(ctx)
    skills = ctx.trace.skills_invoked
    assert "intent-classify" in skills
    assert "knowledge-retrieve" in skills
    assert "answer-compose" in skills
    assert "企业版" in ctx.response or "专业版" in ctx.response
    assert ctx.memory_context.get("source_refs")


def test_ut_s_006_ticket_create_path(orch: SkillOrchestrator):
    ctx = HarnessContext(message="服务器宕机了请尽快处理", session_id="o2")
    ctx = orch.run(ctx)
    assert "ticket-create" in ctx.trace.skills_invoked
    assert "T-" in ctx.response
    assert "ticket-query" not in ctx.trace.skills_invoked


def test_ut_s_007_query_does_not_create(orch: SkillOrchestrator):
    before = len(ticket_api._tickets)
    ctx = HarnessContext(message="帮我查一下工单 T-001 的处理进度", session_id="o3")
    ctx = orch.run(ctx)
    assert "ticket-query" in ctx.trace.skills_invoked
    assert "ticket-create" not in ctx.trace.skills_invoked
    assert len(ticket_api._tickets) == before
    assert "T-001" in ctx.response


def test_complaint_escalation(orch: SkillOrchestrator):
    ctx = HarnessContext(message="太差了，三次没解决，要投诉", session_id="o4")
    ctx = orch.run(ctx)
    assert "escalation-judge" in ctx.trace.skills_invoked
    assert "human-handoff" in ctx.trace.skills_invoked
    assert "人工" in ctx.response or "转接" in ctx.response


def test_ticket_create_fallback(orch: SkillOrchestrator):
    ctx = HarnessContext(message="我要报修", session_id="o5")
    ctx = orch.run(ctx)
    assert "补充" in ctx.response or "标题" in ctx.response
    assert "ticket_id" not in ctx.memory_context
