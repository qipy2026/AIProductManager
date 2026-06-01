"""Agent Router — 封装 Runtime Harness + Skill Orchestrator."""

from __future__ import annotations

from harness.runtime.pipeline import RuntimeHarness
from harness.runtime.trace_store import save_trace
from skills.orchestrator.orchestrator import SkillOrchestrator

from agent.session import AgentSession


class AgentRouter:
    def __init__(self) -> None:
        self.harness = RuntimeHarness()
        self.orchestrator = SkillOrchestrator()

    def chat(self, message: str, session: AgentSession) -> dict:
        session.append_turn("user", message)

        def handler(ctx):
            return self.orchestrator.run(ctx)

        ctx = self.harness.run(
            message,
            session_id=session.session_id,
            user_id=session.user_id,
            skill_handler=handler,
        )
        session.append_turn("assistant", ctx.response)

        save_trace(
            ctx.trace,
            extras={"response": ctx.response, "intent": ctx.memory_context.get("intent", "")},
        )

        from backend.api.ops import index_trace

        index_trace(ctx.trace.trace_id)

        return {
            "response": ctx.response,
            "trace_id": ctx.trace.trace_id,
            "intent": ctx.memory_context.get("intent", ""),
            "blocked": ctx.blocked,
            "skills_invoked": ctx.trace.skills_invoked,
            "sources": ctx.memory_context.get("sources", []),
        }
