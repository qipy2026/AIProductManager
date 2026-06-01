"""LangGraph 路由 Agent — DEV-213."""

from __future__ import annotations

from agent.graph import run_langgraph
from agent.session import AgentSession
from harness.runtime.trace_store import save_trace
from backend.api.ops import index_trace


class RouterAgent:
    """LangGraph 驱动的路由 Agent."""

    def __init__(self) -> None:
        from skills.orchestrator.orchestrator import SkillOrchestrator

        self.orchestrator = SkillOrchestrator()

    def handle(self, message: str, session: AgentSession) -> dict:
        ctx = run_langgraph(
            message,
            session_id=session.session_id,
            user_id=session.user_id,
            orchestrator=self.orchestrator,
        )
        session.append_turn("user", message)
        session.append_turn("assistant", ctx.response)
        save_trace(
            ctx.trace,
            extras={"response": ctx.response, "intent": ctx.memory_context.get("intent", "")},
        )
        index_trace(ctx.trace.trace_id)
        return {
            "response": ctx.response,
            "trace_id": ctx.trace.trace_id,
            "intent": ctx.memory_context.get("intent", ""),
            "skills_invoked": ctx.trace.skills_invoked,
        }
