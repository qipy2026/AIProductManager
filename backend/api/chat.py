"""对话 API — Orchestrator 全链路."""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter
from harness.runtime.context import HarnessContext
from harness.runtime.pipeline import RuntimeHarness
from harness.runtime.trace_store import save_trace
from backend.api.ops import index_trace
from skills.orchestrator.orchestrator import SkillOrchestrator

router = APIRouter()
harness = RuntimeHarness()
orchestrator = SkillOrchestrator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = ""
    user_id: str = ""


class ChatResponse(BaseModel):
    response: str
    trace_id: str
    session_id: str = ""
    blocked: bool = False
    skills_invoked: list[str] = Field(default_factory=list)
    memory_injected: list[str] = Field(default_factory=list)
    intent: str = ""
    confidence: float = 0.0
    sources: list[dict] = Field(default_factory=list)


def _orchestrator_handler(ctx: HarnessContext) -> HarnessContext:
    from backend.config import settings

    if settings.use_langgraph:
        from agent.graph import run_langgraph

        return run_langgraph(
            ctx.message,
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            orchestrator=orchestrator,
        )
    return orchestrator.run(ctx)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or f"sess-{__import__('uuid').uuid4().hex[:12]}"
    from backend.db.conversations import hydrate_working_memory, save_turn

    hydrate_working_memory(session_id)

    ctx = harness.run(
        req.message,
        session_id=session_id,
        user_id=req.user_id,
        skill_handler=_orchestrator_handler,
    )
    intent_result = ctx.memory_context.get("intent_result", {})
    save_trace(
        ctx.trace,
        extras={
            "response": ctx.response,
            "intent": str(intent_result.get("intent", "")),
            "session_id": session_id,
        },
    )
    index_trace(ctx.trace.trace_id)

    sources = ctx.memory_context.get("source_refs", [])
    save_turn(
        session_id=session_id,
        user_id=req.user_id,
        user_message=req.message,
        assistant_message=ctx.response,
        trace_id=ctx.trace.trace_id,
        intent=str(intent_result.get("intent", "")),
        confidence=float(intent_result.get("confidence", 0.0)),
        sources=sources,
        blocked=ctx.blocked,
    )
    return ChatResponse(
        response=ctx.response,
        trace_id=ctx.trace.trace_id,
        session_id=session_id,
        blocked=ctx.blocked,
        skills_invoked=ctx.trace.skills_invoked,
        memory_injected=ctx.trace.memory_injected,
        intent=str(intent_result.get("intent", "")),
        confidence=float(intent_result.get("confidence", 0.0)),
        sources=sources,
    )
