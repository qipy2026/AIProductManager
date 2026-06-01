"""Runtime Harness 主管道."""

from __future__ import annotations

from typing import Any, Callable

from harness.runtime.context import HarnessContext, TraceStep
from harness.runtime.executor import ExecutorConfig, HarnessExecutor
from harness.runtime.guardrail.input import InputGuardrail
from harness.runtime.guardrail.output import OutputGuardrail
from harness.runtime.tool_validator import ToolValidator

SkillHandler = Callable[[HarnessContext], HarnessContext]


class RuntimeHarness:
    """包裹每次 Agent 调用的统一运行时."""

    def __init__(self, executor_config: ExecutorConfig | None = None) -> None:
        self.input_guardrail = InputGuardrail()
        self.output_guardrail = OutputGuardrail()
        self.tool_validator = ToolValidator()
        self.executor = HarnessExecutor(executor_config)

    def run(
        self,
        message: str,
        *,
        session_id: str = "",
        user_id: str = "",
        memory_injector: Callable[[HarnessContext], HarnessContext] | None = None,
        skill_handler: SkillHandler | None = None,
        skill_steps: list[SkillHandler] | None = None,
    ) -> HarnessContext:
        ctx = HarnessContext(
            message=message,
            session_id=session_id,
            user_id=user_id,
        )

        ctx = self.input_guardrail.check(ctx)
        if ctx.blocked:
            return ctx

        if memory_injector:
            ctx = memory_injector(ctx)
            ctx.trace.add_step(
                TraceStep(
                    name="memory_injector",
                    layer="memory",
                    output_summary=f"injected:{','.join(ctx.trace.memory_injected)}",
                    metadata={"layers": list(ctx.trace.memory_injected)},
                )
            )

        if skill_steps:
            result = self.executor.run_chain(ctx, skill_steps)
            ctx = result.context
        elif skill_handler:
            ctx = skill_handler(ctx)

        require_source = ctx.memory_context.get("require_source", False)
        has_source = bool(ctx.memory_context.get("sources"))
        ctx = self.output_guardrail.check(
            ctx, require_source=require_source, has_source=has_source
        )

        return ctx
