"""Working Memory — 会话级上下文."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Message:
    role: str
    content: str
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class WorkingMemory:
    session_id: str
    messages: list[Message] = field(default_factory=list)
    summary: str = ""
    summarize_after: int = 8

    def append(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) >= self.summarize_after and not self.summary:
            self._summarize()

    def _summarize(self) -> None:
        """超过 8 轮触发摘要（Demo：拼接前 3 条）."""
        head = self.messages[:3]
        self.summary = " | ".join(f"{m.role}:{m.content[:30]}" for m in head)

    def to_context(self) -> dict:
        return {
            "recent_messages": [
                {"role": m.role, "content": m.content} for m in self.messages[-4:]
            ],
            "summary": self.summary,
        }


class WorkingMemoryStore:
    def __init__(self) -> None:
        self._sessions: dict[str, WorkingMemory] = {}

    def get(self, session_id: str) -> WorkingMemory:
        if session_id not in self._sessions:
            self._sessions[session_id] = WorkingMemory(session_id=session_id)
        return self._sessions[session_id]

    def clear(self) -> None:
        self._sessions.clear()
