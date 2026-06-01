"""Harness Memory Injector."""

from __future__ import annotations

from harness.runtime.context import HarnessContext
from memory.router.router import MemoryRouter


def build_memory_injector(router: MemoryRouter | None = None):
    router = router or MemoryRouter()

    def inject(ctx: HarnessContext) -> HarnessContext:
        intent = ctx.memory_context.get("intent", "")
        deps = ctx.memory_context.get("_memory_deps", ["working"])
        mem, layers = router.inject(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            message=ctx.message,
            memory_deps=deps,
            intent=intent,
        )
        ctx.memory_context.update(mem)
        ctx.trace.memory_injected = list(dict.fromkeys(ctx.trace.memory_injected + layers))
        return ctx

    return inject
