"""Trace 存储 — 内存 + SQLite/MySQL 运营持久化."""

from __future__ import annotations

from threading import Lock
from typing import Any

from backend.config import settings
from backend.db.store import get_full_store, get_ops_store
from harness.runtime.context import HarnessTrace

_lock = Lock()
_mem: dict[str, dict[str, Any]] = {}


def _persist(data: dict[str, Any]) -> None:
    store = get_full_store() or get_ops_store()
    if store:
        store.init_db()
        store.trace_save(data["trace_id"], data)


def save_trace(trace: HarnessTrace, extras: dict[str, Any] | None = None) -> None:
    data = trace.to_dict()
    if extras:
        data.update(extras)
    _persist(data)
    with _lock:
        _mem[trace.trace_id] = data


def get_trace(trace_id: str) -> dict[str, Any] | None:
    with _lock:
        if trace_id in _mem:
            return _mem[trace_id]
    for getter in (get_full_store, get_ops_store):
        store = getter()
        if store:
            data = store.trace_get(trace_id)
            if data:
                with _lock:
                    _mem[trace_id] = data
                return data
    return None


def list_trace_ids(limit: int = 500) -> list[str]:
    store = get_full_store() or get_ops_store()
    if store:
        ids = store.trace_list(limit)
        if ids:
            return ids
    with _lock:
        return list(_mem.keys())[-limit:]


def clear_traces() -> None:
    with _lock:
        _mem.clear()
