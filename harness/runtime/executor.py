"""Step Limiter + Retry 执行器."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from harness.runtime.context import HarnessContext, TraceStep

StepFn = Callable[[HarnessContext], HarnessContext]


@dataclass
class ExecutorConfig:
    max_steps: int = 10
    timeout_sec: float = 30.0
    fallback_message: str = "处理步骤过多，已为您转接简化流程，请补充关键信息或联系人工客服。"


@dataclass
class ExecutionResult:
    context: HarnessContext
    steps_executed: int = 0
    terminated: bool = False
    termination_reason: str = ""


class HarnessExecutor:
    """执行 Skill 步骤链，含步数限制与超时降级."""

    def __init__(self, config: ExecutorConfig | None = None) -> None:
        self.config = config or ExecutorConfig()

    def run_chain(
        self,
        ctx: HarnessContext,
        steps: list[StepFn],
        *,
        step_names: list[str] | None = None,
    ) -> ExecutionResult:
        start = time.monotonic()
        names = step_names or [f"step_{i}" for i in range(len(steps))]
        executed = 0

        for i, (name, step_fn) in enumerate(zip(names, steps)):
            if executed >= self.config.max_steps:
                return self._terminate(ctx, executed, "max_steps_exceeded")

            elapsed = time.monotonic() - start
            if elapsed >= self.config.timeout_sec:
                return self._terminate(ctx, executed, "timeout")

            try:
                ctx = step_fn(ctx)
                executed += 1
                ctx.trace.add_step(
                    TraceStep(
                        name=f"executor:{name}",
                        layer="skill",
                        output_summary="ok",
                        metadata={"step_index": i, "step_name": name},
                    )
                )
            except Exception as exc:  # noqa: BLE001 — harness 边界捕获
                ctx.trace.add_step(
                    TraceStep(
                        name=f"executor:{name}",
                        layer="skill",
                        output_summary=f"error:{type(exc).__name__}",
                        metadata={"step_index": i, "error": str(exc)[:200]},
                    )
                )
                return self._terminate(ctx, executed, f"step_error:{name}")

            if ctx.blocked:
                return ExecutionResult(
                    context=ctx,
                    steps_executed=executed,
                    terminated=True,
                    termination_reason="blocked",
                )

        return ExecutionResult(context=ctx, steps_executed=executed)

    def _terminate(
        self,
        ctx: HarnessContext,
        executed: int,
        reason: str,
    ) -> ExecutionResult:
        ctx.response = self.config.fallback_message
        ctx.trace.add_step(
            TraceStep(
                name="step_limiter",
                layer="guardrail",
                output_summary=f"terminated:{reason}",
                metadata={"steps_executed": executed, "max_steps": self.config.max_steps},
            )
        )
        ctx.trace.attribution = "流程"
        return ExecutionResult(
            context=ctx,
            steps_executed=executed,
            terminated=True,
            termination_reason=reason,
        )

    def retry(
        self,
        fn: Callable[[], Any],
        *,
        max_attempts: int = 3,
        delay_sec: float = 0.0,
    ) -> tuple[bool, Any]:
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return True, fn()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < max_attempts and delay_sec > 0:
                    time.sleep(delay_sec)
        return False, last_error
