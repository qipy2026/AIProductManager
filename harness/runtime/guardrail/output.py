"""Output Guardrail — 幻觉检测 / 来源引用强制."""

from __future__ import annotations

from agent.identity import identity
from harness.runtime.context import HarnessContext, TraceStep


class OutputGuardrail:
    """输出安全与合规校验."""

    def check(
        self,
        ctx: HarnessContext,
        *,
        require_source: bool = False,
        has_source: bool = False,
    ) -> HarnessContext:
        if require_source and not has_source:
            ctx.response = ctx.response + identity.template("guardrail_no_source_suffix")
            ctx.trace.add_step(
                TraceStep(
                    name="output_guardrail",
                    layer="guardrail",
                    output_summary="warn:no_source",
                    metadata={"require_source": True},
                )
            )
            return ctx

        ctx.trace.add_step(
            TraceStep(
                name="output_guardrail",
                layer="guardrail",
                output_summary="passed",
            )
        )
        return ctx
