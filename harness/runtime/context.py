"""Harness 执行上下文与 Trace 数据结构."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TraceStep:
    name: str
    layer: str  # guardrail | memory | skill | tool | agent
    input_summary: str = ""
    output_summary: str = ""
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessTrace:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    steps: list[TraceStep] = field(default_factory=list)
    skills_invoked: list[str] = field(default_factory=list)
    memory_injected: list[str] = field(default_factory=list)
    attribution: str = ""  # 七层归因标签

    def add_step(self, step: TraceStep) -> None:
        self.steps.append(step)
        if step.layer == "skill":
            skill_id = step.metadata.get("skill_id")
            if skill_id and skill_id not in self.skills_invoked:
                self.skills_invoked.append(skill_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at,
            "steps": [
                {
                    "name": s.name,
                    "layer": s.layer,
                    "input_summary": s.input_summary,
                    "output_summary": s.output_summary,
                    "duration_ms": s.duration_ms,
                    "metadata": s.metadata,
                }
                for s in self.steps
            ],
            "skills_invoked": self.skills_invoked,
            "memory_injected": self.memory_injected,
            "attribution": self.attribution,
        }


@dataclass
class HarnessContext:
    """单次 Agent 调用的 Harness 上下文."""

    message: str
    session_id: str = ""
    user_id: str = ""
    trace: HarnessTrace = field(default_factory=HarnessTrace)
    memory_context: dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    block_reason: str = ""
    response: str = ""

    def __post_init__(self) -> None:
        self.trace.session_id = self.session_id
        self.trace.user_id = self.user_id
