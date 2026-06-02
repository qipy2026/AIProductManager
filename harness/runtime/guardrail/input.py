"""Input Guardrail — 敏感词 / PII / 注入攻击拦截."""

from __future__ import annotations

import re

from agent.identity import identity
from harness.runtime.context import HarnessContext, TraceStep

# 敏感词（Demo 级，生产应接合规词库）
SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(password|密码)\s*[:：=]\s*\S+"),
    re.compile(r"(?i)(my password is|密码是)\s*\S+"),
    re.compile(r"\b\d{15,18}\b"),  # 身份证
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),  # 手机号
]

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions"),
    re.compile(r"(?i)忽略(以上|之前|上面)(的)?(指令|规则|提示)"),
    re.compile(r"(?i)system\s*:\s*"),
]


class InputGuardrail:
    """输入安全校验."""

    def check(self, ctx: HarnessContext) -> HarnessContext:
        text = ctx.message

        for pattern in INJECTION_PATTERNS:
            if pattern.search(text):
                ctx.blocked = True
                ctx.block_reason = "prompt_injection"
                ctx.response = identity.template("guardrail_injection")
                ctx.trace.add_step(
                    TraceStep(
                        name="input_guardrail",
                        layer="guardrail",
                        input_summary=text[:100],
                        output_summary="blocked:injection",
                        metadata={"reason": "prompt_injection"},
                    )
                )
                ctx.trace.attribution = "guardrail"
                return ctx

        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                ctx.blocked = True
                ctx.block_reason = "sensitive_data"
                ctx.response = identity.template("guardrail_sensitive")
                ctx.trace.add_step(
                    TraceStep(
                        name="input_guardrail",
                        layer="guardrail",
                        input_summary="[redacted]",
                        output_summary="blocked:sensitive",
                        metadata={"reason": "sensitive_data"},
                    )
                )
                ctx.trace.attribution = "guardrail"
                return ctx

        ctx.trace.add_step(
            TraceStep(
                name="input_guardrail",
                layer="guardrail",
                input_summary=text[:100],
                output_summary="passed",
            )
        )
        return ctx
