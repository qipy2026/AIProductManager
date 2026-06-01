"""对话历史持久化 — SQLite / MySQL / 内存."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any

from backend.db.store import get_ops_store

_lock = threading.Lock()
_mem_sessions: dict[str, dict[str, Any]] = {}
_mem_messages: dict[str, list[dict[str, Any]]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _title(text: str, n: int = 32) -> str:
    t = text.strip().replace("\n", " ")
    return t[:n] + ("…" if len(t) > n else "")


def _use_db() -> bool:
    return get_ops_store() is not None


def save_turn(
    *,
    session_id: str,
    user_id: str,
    user_message: str,
    assistant_message: str,
    trace_id: str = "",
    intent: str = "",
    confidence: float = 0.0,
    sources: list | None = None,
    blocked: bool = False,
) -> None:
    if not session_id:
        return
    title = _title(user_message)
    ts = _now()
    user_row = {
        "role": "user",
        "content": user_message,
        "trace_id": "",
        "intent": "",
        "confidence": 0.0,
        "sources": [],
        "created_at": ts,
    }
    asst_row = {
        "role": "assistant",
        "content": assistant_message,
        "trace_id": trace_id,
        "intent": intent,
        "confidence": confidence,
        "sources": sources or [],
        "blocked": blocked,
        "created_at": ts,
    }
    with _lock:
        if _use_db():
            store = get_ops_store()
            assert store is not None
            store.conversation_save_turn(
                session_id=session_id,
                user_id=user_id,
                title=title,
                user_row=user_row,
                assistant_row=asst_row,
            )
        else:
            if session_id not in _mem_sessions:
                _mem_sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "title": title,
                    "updated_at": ts,
                    "message_count": 0,
                }
            else:
                _mem_sessions[session_id]["title"] = _mem_sessions[session_id].get("title") or title
                _mem_sessions[session_id]["updated_at"] = ts
            _mem_messages.setdefault(session_id, []).extend([user_row, asst_row])
            _mem_sessions[session_id]["message_count"] = len(_mem_messages[session_id])


def list_sessions(limit: int = 50, user_id: str = "") -> list[dict[str, Any]]:
    with _lock:
        if _use_db():
            store = get_ops_store()
            assert store is not None
            return store.conversation_list(limit=limit, user_id=user_id)
        sessions = list(_mem_sessions.values())
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions[:limit]


def get_messages(session_id: str) -> list[dict[str, Any]]:
    with _lock:
        if _use_db():
            store = get_ops_store()
            assert store is not None
            return store.conversation_get_messages(session_id)
        return list(_mem_messages.get(session_id, []))


def hydrate_working_memory(session_id: str) -> None:
    """续聊时把历史消息灌入 Working Memory（进程内未加载时）."""
    if not session_id:
        return
    from memory.router.router import working_store

    wm = working_store.get(session_id)
    if wm.messages:
        return
    for msg in get_messages(session_id):
        wm.append(msg["role"], msg["content"])


def clear_all() -> None:
    """测试用."""
    with _lock:
        _mem_sessions.clear()
        _mem_messages.clear()
        if _use_db():
            store = get_ops_store()
            assert store is not None
            store.conversation_clear_all()
