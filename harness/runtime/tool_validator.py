"""Tool Validator — JSON Schema 校验 + 重试."""

from __future__ import annotations

from typing import Any

from harness.runtime.context import TraceStep


class ToolValidator:
    """Tool 调用参数校验."""

    MAX_RETRIES = 3

    def validate(
        self,
        tool_name: str,
        params: dict[str, Any],
        schema: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        errors: list[str] = []
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in params or params[field] in (None, ""):
                errors.append(f"missing required field: {field}")

        for key, value in params.items():
            if key not in properties:
                continue
            expected = properties[key].get("type")
            if expected == "string" and not isinstance(value, str):
                errors.append(f"{key}: expected string")
            elif expected == "integer" and not isinstance(value, int):
                errors.append(f"{key}: expected integer")

        return len(errors) == 0, errors

    def validate_with_retry(
        self,
        tool_name: str,
        params: dict[str, Any],
        schema: dict[str, Any],
        trace_steps: list[TraceStep] | None = None,
    ) -> tuple[bool, dict[str, Any], list[str]]:
        current = dict(params)
        all_errors: list[str] = []

        for attempt in range(1, self.MAX_RETRIES + 1):
            ok, errors = self.validate(tool_name, current, schema)
            if ok:
                if trace_steps is not None:
                    trace_steps.append(
                        TraceStep(
                            name="tool_validator",
                            layer="tool",
                            output_summary=f"passed:attempt_{attempt}",
                            metadata={"tool": tool_name, "attempt": attempt},
                        )
                    )
                return True, current, []

            all_errors = errors
            if trace_steps is not None:
                trace_steps.append(
                    TraceStep(
                        name="tool_validator",
                        layer="tool",
                        output_summary=f"failed:attempt_{attempt}",
                        metadata={"tool": tool_name, "errors": errors},
                    )
                )

        return False, current, all_errors
