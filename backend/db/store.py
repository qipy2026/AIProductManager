"""统一 DB 路由 — sqlite / mysql / 无持久化."""

from __future__ import annotations

from typing import Any, Protocol


class OpsStore(Protocol):
    def init_db(self) -> None: ...
    def trace_save(self, trace_id: str, payload: dict[str, Any]) -> None: ...
    def trace_get(self, trace_id: str) -> dict[str, Any] | None: ...
    def trace_list(self, limit: int = 500) -> list[str]: ...
    def badcase_add(self, **kwargs: Any) -> int: ...
    def badcase_list(self, limit: int = 50) -> list[dict[str, Any]]: ...


def _ops_backend() -> str | None:
    from backend.config import settings

    ops = settings.ops_db.strip().lower()
    if ops in ("none", "off", "memory"):
        return None
    if ops:
        return ops
    if settings.storage in ("sqlite", "mysql"):
        return settings.storage
    return "sqlite"  # 默认运营数据落 SQLite


def get_ops_store() -> OpsStore | None:
    backend = _ops_backend()
    if backend == "mysql":
        from backend.db import mysql_store

        return mysql_store
    if backend == "sqlite":
        from backend.db import sqlite_store

        return sqlite_store
    return None


def get_full_store() -> OpsStore | None:
    """Ticket/Episodic 全量持久化（AGENTOPS_STORAGE=sqlite|mysql）."""
    from backend.config import settings

    if settings.storage == "mysql":
        from backend.db import mysql_store

        return mysql_store
    if settings.storage == "sqlite":
        from backend.db import sqlite_store

        return sqlite_store
    return None
