"""Skill 执行器 — 按 Manifest 调度 Handler."""

from __future__ import annotations

import time
from typing import Any

from harness.runtime.context import HarnessContext, TraceStep
from skills.handlers import HANDLERS
from skills.handlers.intent_classify import CLARIFY_FALLBACK
from skills.runtime.registry import SkillRegistry


class SkillExecutor:
    def __init__(self, registry: SkillRegistry | None = None) -> None:
        self.registry = registry or SkillRegistry()

    def invoke(self, skill_id: str, ctx: HarnessContext) -> HarnessContext:
        manifest = self.registry.load(skill_id)
        started = time.perf_counter()

        handler = HANDLERS.get(skill_id)
        if handler is None:
            raise NotImplementedError(f"No handler registered for skill: {skill_id}")

        ctx = handler(ctx)
        elapsed_ms = (time.perf_counter() - started) * 1000

        output = ctx.memory_context.get("intent_result") or {}
        if skill_id in ("ticket-create", "ticket-query"):
            output_summary = ctx.memory_context.get("ticket_id") or ctx.memory_context.get("fallback", "ok")
        elif skill_id == "knowledge-retrieve":
            output_summary = f"hits={len(ctx.memory_context.get('chunks', []))}"
        else:
            output_summary = (
                f"intent={output.get('intent', '?')},conf={output.get('confidence', 0):.2f}"
                if output
                else (ctx.response[:80] if ctx.response else "ok")
            )

        ctx.trace.add_step(
            TraceStep(
                name=f"skill:{skill_id}",
                layer="skill",
                input_summary=ctx.message[:80],
                output_summary=output_summary[:120],
                duration_ms=elapsed_ms,
                metadata={
                    "skill_id": skill_id,
                    "version": manifest["version"],
                    "prompt": manifest.get("prompt_template", ""),
                },
            )
        )
        return ctx

    def format_user_response(self, skill_id: str, ctx: HarnessContext) -> str:
        """将 Skill 输出格式化为用户可见回复（intent-classify 边界外由 API 层承担）."""
        if skill_id != "intent-classify":
            return ctx.response or f"[{skill_id}] 已执行"

        result: dict[str, Any] = ctx.memory_context.get("intent_result", {})
        if result.get("needs_clarify"):
            return CLARIFY_FALLBACK

        intent = result.get("intent", "unknown")
        confidence = float(result.get("confidence", 0))
        from skills.handlers.intent_classify import INTENT_LABELS

        label = INTENT_LABELS.get(intent, intent)
        ticket_mode = result.get("ticket_mode")
        route_hint = ""
        if intent == "ticket" and ticket_mode:
            route_hint = f" → 下一步：ticket-{ticket_mode}（M2 联调）"
        elif intent == "consult":
            route_hint = " → 下一步：knowledge-retrieve（M2 联调）"
        elif intent == "complaint":
            route_hint = " → 下一步：sentiment-analyze（M2 联调）"

        return f"已识别意图：{label}（置信度 {confidence:.0%}）{route_hint}"
