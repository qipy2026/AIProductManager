"""五维断言引擎."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalResult:
    case_id: str
    layer: str
    passed: bool
    failures: list[str] = field(default_factory=list)


def check_case(case: dict, *, skills: list[str], memory_injected: list[str],
                 response: str, blocked: bool, intent: str = "") -> EvalResult:
    cid = case.get("id", "?")
    layer = case.get("layer", "?")
    failures: list[str] = []
    assertions: dict[str, Any] = case.get("assertions", {})

    if assertions.get("blocked") is True and not blocked:
        failures.append("expected blocked=true")
    if assertions.get("blocked") is False and blocked:
        failures.append("expected not blocked")

    skill_a = assertions.get("skill", {})
    for s in skill_a.get("must_invoke", []) or []:
        if s not in skills:
            failures.append(f"must_invoke missing: {s}")
    for s in skill_a.get("must_not_invoke", []) or []:
        if s in skills:
            failures.append(f"must_not_invoke violated: {s}")

    mem_a = assertions.get("memory", {})
    for m in mem_a.get("must_inject", []) or []:
        if m not in memory_injected:
            failures.append(f"must_inject missing: {m}")
    for m in mem_a.get("must_not_inject", []) or []:
        if m in memory_injected:
            failures.append(f"must_not_inject violated: {m}")

    resp_a = assertions.get("response", {})
    for kw in resp_a.get("must_contain", []) or []:
        s = str(kw) if kw is not None else ""
        if s and s not in response:
            failures.append(f"response must contain: {s}")
    for kw in resp_a.get("must_not_contain", []) or []:
        s = str(kw) if kw is not None else ""
        if s and s in response:
            failures.append(f"response must not contain: {s}")

    intent_a = assertions.get("intent", {})
    if "equals" in intent_a and intent != intent_a["equals"]:
        failures.append(f"intent expected {intent_a['equals']} got {intent}")

    src_a = assertions.get("source", {})
    if src_a.get("min_count"):
        # sources checked via response markers
        if response.count("[1]") < 1 and "来源" not in response and "📎" not in response:
            if src_a["min_count"] > 0:
                failures.append("source refs missing")

    return EvalResult(case_id=cid, layer=layer, passed=len(failures) == 0, failures=failures)
