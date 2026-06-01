"""Agent 会话上下文."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentSession:
    session_id: str
    user_id: str = ""
    turns: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def append_turn(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
