"""LangGraph Agent 编排 — 包装 SkillOrchestrator."""

from __future__ import annotations

from typing import Any, TypedDict

from harness.runtime.context import HarnessContext
from skills.orchestrator.orchestrator import SkillOrchestrator


class AgentGraphState(TypedDict, total=False):
    message: str
    session_id: str
    user_id: str
    ctx: HarnessContext
    route_key: str
    done: bool


def build_langgraph_agent(orchestrator: SkillOrchestrator | None = None):
    """构建 LangGraph StateGraph；未安装 langgraph 时抛 ImportError."""
    from langgraph.graph import END, StateGraph

    orch = orchestrator or SkillOrchestrator()

    def init_state(state: AgentGraphState) -> AgentGraphState:
        ctx = HarnessContext(
            message=state["message"],
            session_id=state.get("session_id", ""),
            user_id=state.get("user_id", ""),
        )
        ctx.memory_context["_memory_deps"] = ["working"]
        return {**state, "ctx": ctx, "done": False}

    def classify_node(state: AgentGraphState) -> AgentGraphState:
        ctx = state["ctx"]
        ctx = orch.executor.invoke("intent-classify", ctx)
        result = ctx.memory_context.get("intent_result", {})
        if result.get("needs_clarify"):
            ctx.memory_context["_memory_deps"] = ["working"]
            ctx = orch.memory_injector(ctx)
            ctx.response = CLARIFY_FALLBACK
            return {**state, "ctx": ctx, "route_key": "clarify", "done": True}
        route_key = orch._route_key(result, ctx.message)
        return {**state, "ctx": ctx, "route_key": route_key}

    def orchestrate_node(state: AgentGraphState) -> AgentGraphState:
        ctx = state["ctx"]
        route_key = state.get("route_key", "clarify")
        ctx = orch.execute_route(ctx, route_key)
        return {**state, "ctx": ctx, "done": True}

    def after_classify(state: AgentGraphState) -> str:
        return "end" if state.get("done") else "orchestrate"

    g = StateGraph(AgentGraphState)
    g.add_node("init", init_state)
    g.add_node("classify", classify_node)
    g.add_node("orchestrate", orchestrate_node)
    g.set_entry_point("init")
    g.add_edge("init", "classify")
    g.add_conditional_edges("classify", after_classify, {"orchestrate": "orchestrate", "end": END})
    g.add_edge("orchestrate", END)
    return g.compile()


def run_langgraph(
    message: str,
    *,
    session_id: str = "",
    user_id: str = "",
    orchestrator: SkillOrchestrator | None = None,
) -> HarnessContext:
    """LangGraph 入口；失败时回退 Orchestrator."""
    try:
        graph = build_langgraph_agent(orchestrator)
        out: dict[str, Any] = graph.invoke(
            {"message": message, "session_id": session_id, "user_id": user_id}
        )
        return out["ctx"]
    except ImportError:
        orch = orchestrator or SkillOrchestrator()
        ctx = HarnessContext(message=message, session_id=session_id, user_id=user_id)
        return orch.run(ctx)
