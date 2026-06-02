"""SQLite 持久化 — Trace / Ticket / Episodic / BadCase."""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from backend.config import settings

_lock = threading.Lock()
_initialized = False


def _db_path() -> Path:
    p = Path(settings.db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(_db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    global _initialized
    with _lock:
        if _initialized:
            return
        with get_conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    user_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    status TEXT,
                    priority TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS episodic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    summary TEXT,
                    ticket_ids TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS badcases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    case_id TEXT,
                    layer TEXT,
                    attribution TEXT,
                    note TEXT,
                    failures TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    title TEXT,
                    updated_at TEXT,
                    message_count INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    trace_id TEXT,
                    intent TEXT,
                    confidence REAL DEFAULT 0,
                    sources TEXT,
                    blocked INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
                """
            )
            # 种子工单
            conn.execute(
                "INSERT OR IGNORE INTO tickets VALUES (?,?,?,?,?)",
                ("T-001", "服务器宕机", "in_progress", "urgent", ""),
            )
            conn.execute(
                "INSERT OR IGNORE INTO tickets VALUES (?,?,?,?,?)",
                ("T-002", "网络异常", "new", "normal", ""),
            )
        _initialized = True


def trace_save(trace_id: str, payload: dict[str, Any]) -> None:
    init_db()
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO traces(trace_id, session_id, user_id, payload) VALUES (?,?,?,?)",
            (
                trace_id,
                payload.get("session_id", ""),
                payload.get("user_id", ""),
                json.dumps(payload, ensure_ascii=False),
            ),
        )


def trace_get(trace_id: str) -> dict[str, Any] | None:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT payload FROM traces WHERE trace_id=?", (trace_id,)).fetchone()
    return json.loads(row["payload"]) if row else None


def trace_list(limit: int = 500) -> list[str]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT trace_id FROM traces ORDER BY rowid DESC LIMIT ?", (limit,)
        ).fetchall()
    return [r["trace_id"] for r in rows]


def badcase_add(
    *,
    trace_id: str = "",
    case_id: str = "",
    layer: str = "",
    attribution: str = "",
    note: str = "",
    failures: list[str] | None = None,
) -> int:
    init_db()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO badcases(trace_id, case_id, layer, attribution, note, failures)
               VALUES (?,?,?,?,?,?)""",
            (
                trace_id,
                case_id,
                layer,
                attribution,
                note,
                json.dumps(failures or [], ensure_ascii=False),
            ),
        )
        return int(cur.lastrowid)


def badcase_list(limit: int = 50) -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM badcases ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["failures"] = json.loads(item.get("failures") or "[]")
        out.append(item)
    return out


def badcase_update(badcase_id: int, **fields: str) -> dict[str, Any] | None:
    init_db()
    allowed = {"attribution", "note", "trace_id", "case_id", "layer"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM badcases WHERE id=?", (badcase_id,)).fetchone()
        if not row:
            return None
        sets = ", ".join(f"{k}=?" for k in updates)
        conn.execute(
            f"UPDATE badcases SET {sets} WHERE id=?",
            (*updates.values(), badcase_id),
        )
        row = conn.execute("SELECT * FROM badcases WHERE id=?", (badcase_id,)).fetchone()
    item = dict(row)
    item["failures"] = json.loads(item.get("failures") or "[]")
    return item


def badcase_delete_by_note_prefix(prefix: str) -> int:
    init_db()
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM badcases WHERE note LIKE ?", (f"{prefix}%",))
        return int(cur.rowcount)


def badcase_reclassify_all() -> dict[str, Any]:
    from backend.badcase.attribution_infer import infer_attribution_from_badcase

    init_db()
    updated = 0
    by_attribution: dict[str, int] = {}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, case_id, attribution, layer, note, failures FROM badcases"
        ).fetchall()
        for r in rows:
            item = dict(r)
            item["failures"] = json.loads(item.get("failures") or "[]")
            new_attr = infer_attribution_from_badcase(item, force=True)
            by_attribution[new_attr] = by_attribution.get(new_attr, 0) + 1
            if new_attr != item["attribution"]:
                conn.execute(
                    "UPDATE badcases SET attribution=? WHERE id=?",
                    (new_attr, item["id"]),
                )
                updated += 1
    return {
        "updated": updated,
        "total": len(rows),
        "by_attribution": by_attribution,
    }


def trace_count() -> int:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM traces").fetchone()
    return int(row["c"])


def badcase_count() -> int:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM badcases").fetchone()
    return int(row["c"])


def ticket_get(ticket_id: str) -> dict[str, Any] | None:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id.upper(),)).fetchone()
    return dict(row) if row else None


def ticket_list() -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def ticket_create(title: str, priority: str = "normal") -> dict[str, Any]:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM tickets ORDER BY id DESC LIMIT 1").fetchone()
        num = 100
        if row:
            try:
                num = int(str(row["id"]).split("-")[1])
            except (IndexError, ValueError):
                pass
        tid = f"T-{num + 1:03d}"
        conn.execute(
            "INSERT INTO tickets(id, title, status, priority) VALUES (?,?,?,?)",
            (tid, title, "new", priority),
        )
    return {"id": tid, "title": title, "status": "new", "priority": priority}


def ticket_update(ticket_id: str, **fields: str) -> dict[str, Any] | None:
    init_db()
    t = ticket_get(ticket_id)
    if not t:
        return None
    status = fields.get("status", t["status"])
    with get_conn() as conn:
        conn.execute(
            "UPDATE tickets SET status=? WHERE id=?",
            (status, ticket_id.upper()),
        )
    t["status"] = status
    return t


def ticket_clear_seed() -> None:
    """Eval 重置 — 仅保留种子工单."""
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM tickets WHERE id NOT IN ('T-001','T-002')")
        conn.execute(
            "UPDATE tickets SET status='in_progress' WHERE id='T-001'"
        )
        conn.execute("UPDATE tickets SET status='new' WHERE id='T-002'")


def episodic_write(user_id: str, summary: str, ticket_ids: list[str]) -> None:
    init_db()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO episodic(user_id, summary, ticket_ids) VALUES (?,?,?)",
            (user_id, summary, json.dumps(ticket_ids)),
        )


def episodic_read(user_id: str) -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT summary, ticket_ids, created_at FROM episodic WHERE user_id=? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [
        {
            "summary": r["summary"],
            "ticket_ids": json.loads(r["ticket_ids"] or "[]"),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def episodic_clear() -> None:
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM episodic")


def _row_to_message(r: sqlite3.Row) -> dict[str, Any]:
    return {
        "role": r["role"],
        "content": r["content"],
        "trace_id": r["trace_id"] or "",
        "intent": r["intent"] or "",
        "confidence": float(r["confidence"] or 0),
        "sources": json.loads(r["sources"] or "[]"),
        "blocked": bool(r["blocked"]),
        "created_at": r["created_at"],
    }


def conversation_save_turn(
    *,
    session_id: str,
    user_id: str,
    title: str,
    user_row: dict[str, Any],
    assistant_row: dict[str, Any],
) -> None:
    init_db()
    updated = user_row.get("created_at", "")
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO chat_sessions(session_id, user_id, title, updated_at, message_count)
               VALUES (?,?,?,?,2)
               ON CONFLICT(session_id) DO UPDATE SET
                 updated_at=excluded.updated_at,
                 message_count=message_count+2""",
            (session_id, user_id, title, updated),
        )
        for row in (user_row, assistant_row):
            conn.execute(
                """INSERT INTO chat_messages
                   (session_id, role, content, trace_id, intent, confidence, sources, blocked, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    session_id,
                    row["role"],
                    row["content"],
                    row.get("trace_id", ""),
                    row.get("intent", ""),
                    row.get("confidence", 0),
                    json.dumps(row.get("sources") or [], ensure_ascii=False),
                    1 if row.get("blocked") else 0,
                    row.get("created_at", updated),
                ),
            )


def conversation_list(limit: int = 50, user_id: str = "") -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        if user_id:
            rows = conn.execute(
                """SELECT session_id, user_id, title, updated_at, message_count
                   FROM chat_sessions WHERE user_id=? ORDER BY updated_at DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT session_id, user_id, title, updated_at, message_count
                   FROM chat_sessions ORDER BY updated_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def conversation_get_messages(session_id: str) -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT role, content, trace_id, intent, confidence, sources, blocked, created_at
               FROM chat_messages WHERE session_id=? ORDER BY id""",
            (session_id,),
        ).fetchall()
    return [_row_to_message(r) for r in rows]


def conversation_clear_all() -> None:
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM chat_messages")
        conn.execute("DELETE FROM chat_sessions")
