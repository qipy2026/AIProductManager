"""Episodic Memory — 内存 + SQLite 双写."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from backend.config import settings

TTL_DAYS = 90
_PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")


@dataclass
class EpisodicRecord:
    user_id: str
    summary: str
    ticket_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) - self.created_at > timedelta(days=TTL_DAYS)


def redact_pii(text: str) -> str:
    return _PHONE.sub("[REDACTED]", text)


class EpisodicMemoryStore:
    def __init__(self) -> None:
        self._records: dict[str, list[EpisodicRecord]] = {}

    def write(self, user_id: str, summary: str, ticket_ids: list[str] | None = None) -> None:
        clean = redact_pii(summary)
        rec = EpisodicRecord(user_id=user_id, summary=clean, ticket_ids=ticket_ids or [])
        self._records.setdefault(user_id, []).append(rec)
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            sqlite_store.episodic_write(user_id, clean, ticket_ids or [])
        elif settings.storage == "mysql":
            from backend.db import mysql_store

            mysql_store.episodic_write(user_id, clean, ticket_ids or [])

    def read(self, user_id: str) -> list[dict]:
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            rows = sqlite_store.episodic_read(user_id)
            if rows:
                return rows
        self._purge_expired(user_id)
        return [
            {"summary": r.summary, "ticket_ids": r.ticket_ids, "created_at": r.created_at.isoformat()}
            for r in self._records.get(user_id, [])
        ]

    def _purge_expired(self, user_id: str) -> None:
        if user_id not in self._records:
            return
        self._records[user_id] = [r for r in self._records[user_id] if not r.is_expired()]

    def clear(self) -> None:
        self._records.clear()
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            sqlite_store.episodic_clear()
