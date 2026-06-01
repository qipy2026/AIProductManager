"""Mock 工单 API — 内存 + SQLite."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.config import settings


@dataclass
class Ticket:
    id: str
    title: str
    status: str = "new"
    priority: str = "normal"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TicketMockAPI:
    def __init__(self) -> None:
        self._tickets: dict[str, Ticket] = {
            "T-001": Ticket(id="T-001", title="服务器宕机", status="in_progress"),
            "T-002": Ticket(id="T-002", title="网络异常", status="new"),
        }
        self._counter = 100

    def get(self, ticket_id: str) -> Ticket | None:
        if settings.storage == "mysql":
            from backend.db import mysql_store

            row = mysql_store.ticket_get(ticket_id)
            if row:
                return Ticket(id=row["id"], title=row["title"], status=row["status"], priority=row.get("priority", "normal"))
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            row = sqlite_store.ticket_get(ticket_id)
            if row:
                return Ticket(
                    id=row["id"],
                    title=row["title"],
                    status=row["status"],
                    priority=row.get("priority", "normal"),
                )
        return self._tickets.get(ticket_id.upper())

    def create(self, title: str, priority: str = "normal", **_: str) -> Ticket:
        if settings.storage == "mysql":
            from backend.db import mysql_store

            row = mysql_store.ticket_create(title, priority)
            t = Ticket(id=row["id"], title=row["title"], status=row["status"], priority=row["priority"])
            self._tickets[t.id] = t
            return t
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            row = sqlite_store.ticket_create(title, priority)
            t = Ticket(id=row["id"], title=row["title"], status=row["status"], priority=row["priority"])
            self._tickets[t.id] = t
            return t
        self._counter += 1
        tid = f"T-{self._counter:03d}"
        t = Ticket(id=tid, title=title, priority=priority)
        self._tickets[tid] = t
        return t

    def update(self, ticket_id: str, **fields: str) -> Ticket | None:
        if settings.storage == "mysql":
            from backend.db import mysql_store

            row = mysql_store.ticket_update(ticket_id, **fields)
            if row:
                t = Ticket(id=row["id"], title=row["title"], status=row["status"])
                self._tickets[t.id] = t
                return t
            return None
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            row = sqlite_store.ticket_update(ticket_id, **fields)
            if row:
                t = Ticket(id=row["id"], title=row["title"], status=row["status"])
                self._tickets[t.id] = t
                return t
            return None
        t = self.get(ticket_id)
        if not t:
            return None
        for k, v in fields.items():
            if hasattr(t, k):
                setattr(t, k, v)
        if fields.get("status") == "closed":
            t.status = "closed"
        return t

    def extract_ticket_id(self, message: str) -> str | None:
        m = re.search(r"T-\d+", message, re.I)
        return m.group(0).upper() if m else None

    def clear(self) -> None:
        self._tickets = {
            "T-001": Ticket(id="T-001", title="服务器宕机", status="in_progress"),
            "T-002": Ticket(id="T-002", title="网络异常", status="new"),
        }
        self._counter = 100
        if settings.storage == "sqlite":
            from backend.db import sqlite_store

            sqlite_store.ticket_clear_seed()
        elif settings.storage == "mysql":
            from backend.db import mysql_store

            mysql_store.ticket_clear_seed()


ticket_api = TicketMockAPI()
