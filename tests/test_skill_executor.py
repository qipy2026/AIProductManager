"""Skill Executor 测试 — UT-S-003~004."""

import pytest

from harness.runtime.context import HarnessContext
from harness.runtime.trace_store import clear_traces
from skills.handlers.intent_classify import classify_message
from skills.runtime.executor import SkillExecutor


@pytest.fixture(autouse=True)
def _clean_traces():
    clear_traces()
    yield
    clear_traces()


def test_ut_s_003_single_skill_invoke_contract():
    """UT-S-003：intent-classify 输入输出契约."""
    executor = SkillExecutor()
    ctx = HarnessContext(message="企业版和专业版有什么区别？", session_id="s1")
    ctx = executor.invoke("intent-classify", ctx)

    result = ctx.memory_context["intent_result"]
    assert result["intent"] == "consult"
    assert result["confidence"] >= 0.85
    assert result["needs_clarify"] is False
    assert "intent-classify" in ctx.trace.skills_invoked

    response = executor.format_user_response("intent-classify", ctx)
    assert "产品咨询" in response
    assert "置信度" in response


def test_ut_s_004_fallback_clarify_on_ambiguous():
    """UT-S-004：低置信 / 模糊输入 → Fallback 澄清话术."""
    executor = SkillExecutor()
    ctx = HarnessContext(message="帮我看看", session_id="s2")
    ctx = executor.invoke("intent-classify", ctx)

    result = ctx.memory_context["intent_result"]
    assert result["needs_clarify"] is True
    assert result["confidence"] < 0.5

    response = executor.format_user_response("intent-classify", ctx)
    assert "咨询产品问题" in response or "补充更多信息" in response


@pytest.mark.parametrize(
    "message,expected_intent",
    [
        ("帮我查一下工单 T-001 的处理进度", "ticket"),
        ("我要报修，设备无法启动", "ticket"),
        ("太差了，要投诉", "complaint"),
        ("我要退款", "refund"),
        ("今天天气怎么样", "chitchat"),
        ("嗯", "unknown"),
    ],
)
def test_intent_classify_rules(message: str, expected_intent: str):
    result = classify_message(message)
    assert result.intent == expected_intent


def test_invoke_unknown_skill_raises():
    executor = SkillExecutor()
    ctx = HarnessContext(message="hello")
    with pytest.raises((NotImplementedError, FileNotFoundError)):
        executor.invoke("nonexistent-skill-xyz", ctx)
