"""Trace Replay Diff — 同输入重跑并对比 Skill/回复差异."""

from __future__ import annotations

from harness.runtime.pipeline import RuntimeHarness
from skills.orchestrator.orchestrator import SkillOrchestrator


def replay_diff(message: str, *, session_id: str = "replay", user_id: str = "", baseline: dict | None = None) -> dict:
    orchestrator = SkillOrchestrator()
    harness = RuntimeHarness()

    def handler(ctx):
        return orchestrator.run(ctx)

    ctx = harness.run(message, session_id=session_id, user_id=user_id, skill_handler=handler)
    current = {
        "skills_invoked": list(ctx.trace.skills_invoked),
        "response": ctx.response,
        "intent": ctx.memory_context.get("intent", ""),
        "memory_injected": list(ctx.trace.memory_injected),
    }
    diff: dict = {"current": current, "baseline": baseline, "changes": []}
    if baseline:
        if baseline.get("skills_invoked") != current["skills_invoked"]:
            diff["changes"].append(
                {
                    "field": "skills_invoked",
                    "before": baseline.get("skills_invoked"),
                    "after": current["skills_invoked"],
                }
            )
        if baseline.get("response") != current["response"]:
            diff["changes"].append(
                {
                    "field": "response",
                    "before": (baseline.get("response") or "")[:200],
                    "after": current["response"][:200],
                }
            )
        if baseline.get("intent") != current["intent"]:
            diff["changes"].append(
                {
                    "field": "intent",
                    "before": baseline.get("intent"),
                    "after": current["intent"],
                }
            )
    diff["has_diff"] = len(diff["changes"]) > 0
    return diff
