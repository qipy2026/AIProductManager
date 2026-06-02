"""Skill Orchestrator — intent → Skill 链调度."""

from __future__ import annotations

from pathlib import Path

import yaml

from agent.identity import identity
from harness.runtime.context import HarnessContext
from harness.runtime.memory_injector import build_memory_injector
from memory.router.router import MemoryRouter
from skills.handlers.intent_classify import CLARIFY_FALLBACK, INTENT_LABELS
from skills.runtime.executor import SkillExecutor
from skills.runtime.registry import SkillRegistry

GRAPH_PATH = Path(__file__).resolve().parent / "graph.yaml"


class SkillOrchestrator:
    def __init__(
        self,
        executor: SkillExecutor | None = None,
        router: MemoryRouter | None = None,
    ) -> None:
        self.executor = executor or SkillExecutor()
        self.memory_router = router or MemoryRouter()
        self.memory_injector = build_memory_injector(self.memory_router)
        self._graph = self._load_graph()

    def _load_graph(self) -> dict:
        with GRAPH_PATH.open(encoding="utf-8") as f:
            return yaml.safe_load(f)["routes"]

    def run(self, ctx: HarnessContext) -> HarnessContext:
        ctx.memory_context["_memory_deps"] = ["working"]
        ctx = self.executor.invoke("intent-classify", ctx)

        result = ctx.memory_context.get("intent_result", {})
        if result.get("needs_clarify"):
            ctx.memory_context["_memory_deps"] = ["working"]
            ctx = self.memory_injector(ctx)
            ctx.response = CLARIFY_FALLBACK
            return ctx

        route_key = self._route_key(result, ctx.message)
        return self.execute_route(ctx, route_key)

    def execute_route(self, ctx: HarnessContext, route_key: str) -> HarnessContext:
        route = self._graph.get(route_key, self._graph["clarify"])
        result = ctx.memory_context.get("intent_result", {})
        ctx.memory_context["intent"] = result.get("intent", "")

        ctx.memory_context["_memory_deps"] = route.get("memory_deps", ["working"])
        ctx = self.memory_injector(ctx)

        for skill_id in route.get("skills", []):
            ctx = self.executor.invoke(skill_id, ctx)
            if ctx.memory_context.get("fallback"):
                break

        if not ctx.response and route_key == "complaint_judge":
            ctx.response = identity.template("complaint_judge")

        if not ctx.response and route_key == "crm":
            pass

        if not ctx.response and route_key == "chitchat":
            from backend.llm.adapter import llm

            reply = llm.chat_reply(ctx.message) if llm.enabled() else ""
            ctx.response = reply or identity.template("chitchat_greeting")

        if not ctx.response and route_key == "clarify":
            ctx.response = CLARIFY_FALLBACK

        if ctx.user_id and ctx.memory_context.get("ticket_id"):
            from memory.router.router import episodic_store

            episodic_store.write(
                ctx.user_id,
                f"用户操作工单 {ctx.memory_context['ticket_id']}",
                [ctx.memory_context["ticket_id"]],
            )

        return ctx

    def _route_key(self, result: dict, message: str = "") -> str:
        intent = result.get("intent", "unknown")
        if "生气" in message and "订单" in message and "投诉" not in message:
            return "angry_ticket"
        if intent == "compliance":
            return "compliance"
        if intent == "crm":
            return "crm"
        if intent == "ticket":
            mode = result.get("ticket_mode", "query")
            if mode == "update":
                return "ticket_update"
            return "ticket_query" if mode == "query" else "ticket_create"
        if intent == "consult":
            return "consult_vip" if "VIP" in message.upper() else "consult"
        if intent == "complaint":
            if "投诉" in message or "太差" in message:
                return "complaint"
            return "complaint_judge"
        if intent == "chitchat":
            return "chitchat"
        if intent in self._graph:
            return intent
        return "clarify"
