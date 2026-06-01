"""intent-classify Skill 级回归（ST × 25）— M1 必交付."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from harness.runtime.context import HarnessContext
from skills.handlers.intent_classify import classify_intent
from skills.runtime.executor import SkillExecutor

ST_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "skills" / "intent-classify"


def _load_cases() -> list[dict]:
    cases = []
    for path in sorted(ST_DIR.glob("ST-IC-*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data["_file"] = path.name
        cases.append(data)
    return cases


CASES = _load_cases()


@pytest.fixture(scope="module")
def executor() -> SkillExecutor:
    return SkillExecutor()


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_st_intent_classify_regression(case: dict, executor: SkillExecutor) -> None:
    """ST：意图 + 置信度 + 边界（不产 Tool / Skill 层不产用户回复）."""
    message = case["input"]["message"]
    expected = case["assertions"]

    ctx = HarnessContext(message=message, session_id=f"st-{case['id']}")
    ctx = executor.invoke("intent-classify", ctx)

    result = ctx.memory_context["intent_result"]
    assert result["intent"] == expected["intent"], (
        f"{case['_file']}: intent {result['intent']} != {expected['intent']}"
    )
    assert result["confidence"] >= expected["min_confidence"]
    assert result["needs_clarify"] == expected["needs_clarify"]

    boundary = expected.get("boundary", {})
    if boundary.get("must_not_set_response"):
        # handler 层不写 response，仅 memory_context
        assert not ctx.response or ctx.response == ""

    assert "intent-classify" in ctx.trace.skills_invoked


def test_st_suite_count():
    assert len(CASES) == 25, f"expected 25 ST cases, got {len(CASES)}"


def test_st_pass_rate_threshold():
    """M1 门禁：intent-classify ST ≥85%（25 条中至少 22 条逻辑正确）."""
    passed = 0
    executor = SkillExecutor()
    for case in CASES:
        try:
            ctx = HarnessContext(message=case["input"]["message"])
            ctx = executor.invoke("intent-classify", ctx)
            result = ctx.memory_context["intent_result"]
            exp = case["assertions"]
            if (
                result["intent"] == exp["intent"]
                and result["confidence"] >= exp["min_confidence"]
                and result["needs_clarify"] == exp["needs_clarify"]
            ):
                passed += 1
        except AssertionError:
            pass
    rate = passed / len(CASES)
    assert rate >= 0.85, f"ST pass rate {rate:.0%} < 85% ({passed}/{len(CASES)})"
