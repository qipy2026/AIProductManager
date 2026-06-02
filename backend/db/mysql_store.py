"""MySQL 持久化 — 供 WSL / 生产环境运营数据."""

from __future__ import annotations

import json
import threading
from typing import Any

from backend.config import settings

_lock = threading.Lock()
_initialized = False

_SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(128),
    user_id VARCHAR(128),
    payload JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tickets (
    id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(255),
    status VARCHAR(32),
    priority VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS episodic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    summary TEXT,
    ticket_ids JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS badcases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trace_id VARCHAR(64),
    case_id VARCHAR(64),
    layer VARCHAR(16),
    attribution VARCHAR(64),
    note TEXT,
    failures JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id VARCHAR(128),
    title VARCHAR(255),
    updated_at VARCHAR(64),
    message_count INT DEFAULT 0
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    trace_id VARCHAR(64),
    intent VARCHAR(32),
    confidence DOUBLE DEFAULT 0,
    sources JSON,
    blocked TINYINT DEFAULT 0,
    created_at VARCHAR(64),
    INDEX idx_chat_session (session_id)
);
"""


def _connect():
    import pymysql

    return pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def init_db() -> None:
    global _initialized
    with _lock:
        if _initialized:
            return
        conn = _connect()
        try:
            with conn.cursor() as cur:
                for stmt in _SCHEMA.strip().split(";"):
                    s = stmt.strip()
                    if s:
                        cur.execute(s)
                cur.execute(
                    "INSERT IGNORE INTO tickets (id, title, status, priority) VALUES (%s,%s,%s,%s)",
                    ("T-001", "服务器宕机", "in_progress", "urgent"),
                )
                cur.execute(
                    "INSERT IGNORE INTO tickets (id, title, status, priority) VALUES (%s,%s,%s,%s)",
                    ("T-002", "网络异常", "new", "normal"),
                )
        finally:
            conn.close()
        _initialized = True


def trace_save(trace_id: str, payload: dict[str, Any]) -> None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO traces(trace_id, session_id, user_id, payload)
                   VALUES (%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE session_id=VALUES(session_id),
                   user_id=VALUES(user_id), payload=VALUES(payload)""",
                (
                    trace_id,
                    payload.get("session_id", ""),
                    payload.get("user_id", ""),
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
    finally:
        conn.close()


def trace_get(trace_id: str) -> dict[str, Any] | None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM traces WHERE trace_id=%s", (trace_id,))
            row = cur.fetchone()
        if not row:
            return None
        payload = row["payload"]
        if isinstance(payload, str):
            return json.loads(payload)
        return payload
    finally:
        conn.close()


def trace_list(limit: int = 500) -> list[str]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT trace_id FROM traces ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            rows = cur.fetchall()
        return [r["trace_id"] for r in rows]
    finally:
        conn.close()


def trace_count() -> int:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM traces")
            return int(cur.fetchone()["c"])
    finally:
        conn.close()


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
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO badcases(trace_id, case_id, layer, attribution, note, failures)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
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
    finally:
        conn.close()


def badcase_list(limit: int = 50) -> list[dict[str, Any]]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM badcases ORDER BY id DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
        out = []
        for r in rows:
            item = dict(r)
            fx = item.get("failures")
            if isinstance(fx, str):
                item["failures"] = json.loads(fx or "[]")
            out.append(item)
        return out
    finally:
        conn.close()


def badcase_update(badcase_id: int, **fields: str) -> dict[str, Any] | None:
    init_db()
    allowed = {"attribution", "note", "trace_id", "case_id", "layer"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return None
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM badcases WHERE id=%s", (badcase_id,))
            if not cur.fetchone():
                return None
            sets = ", ".join(f"{k}=%s" for k in updates)
            cur.execute(
                f"UPDATE badcases SET {sets} WHERE id=%s",
                (*updates.values(), badcase_id),
            )
            cur.execute("SELECT * FROM badcases WHERE id=%s", (badcase_id,))
            row = cur.fetchone()
        item = dict(row)
        fx = item.get("failures")
        if isinstance(fx, str):
            item["failures"] = json.loads(fx or "[]")
        return item
    finally:
        conn.close()


def badcase_delete_by_note_prefix(prefix: str) -> int:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM badcases WHERE note LIKE %s", (f"{prefix}%",))
            return int(cur.rowcount)
    finally:
        conn.close()


def badcase_reclassify_all() -> dict[str, Any]:
    from backend.badcase.attribution_infer import infer_attribution_from_badcase

    init_db()
    updated = 0
    by_attribution: dict[str, int] = {}
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, case_id, attribution, layer, note, failures FROM badcases")
            rows = cur.fetchall()
            for r in rows:
                item = dict(r)
                fx = item.get("failures")
                if isinstance(fx, str):
                    item["failures"] = json.loads(fx or "[]")
                new_attr = infer_attribution_from_badcase(item, force=True)
                by_attribution[new_attr] = by_attribution.get(new_attr, 0) + 1
                if new_attr != item["attribution"]:
                    cur.execute(
                        "UPDATE badcases SET attribution=%s WHERE id=%s",
                        (new_attr, item["id"]),
                    )
                    updated += 1
        return {
            "updated": updated,
            "total": len(rows),
            "by_attribution": by_attribution,
        }
    finally:
        conn.close()


def badcase_count() -> int:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM badcases")
            return int(cur.fetchone()["c"])
    finally:
        conn.close()


# Ticket / episodic — 与 sqlite 接口对齐，供 AGENTOPS_STORAGE=mysql 时使用
def ticket_get(ticket_id: str) -> dict[str, Any] | None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE id=%s", (ticket_id.upper(),))
            return cur.fetchone()
    finally:
        conn.close()


def ticket_list() -> list[dict[str, Any]]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets ORDER BY id")
            return list(cur.fetchall())
    finally:
        conn.close()


def ticket_create(title: str, priority: str = "normal") -> dict[str, Any]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM tickets ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            num = 100
            if row:
                try:
                    num = int(str(row["id"]).split("-")[1])
                except (IndexError, ValueError):
                    pass
            tid = f"T-{num + 1:03d}"
            cur.execute(
                "INSERT INTO tickets(id, title, status, priority) VALUES (%s,%s,%s,%s)",
                (tid, title, "new", priority),
            )
        return {"id": tid, "title": title, "status": "new", "priority": priority}
    finally:
        conn.close()


def ticket_update(ticket_id: str, **fields: str) -> dict[str, Any] | None:
    t = ticket_get(ticket_id)
    if not t:
        return None
    status = fields.get("status", t["status"])
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, ticket_id.upper()))
        t["status"] = status
        return t
    finally:
        conn.close()


def ticket_clear_seed() -> None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tickets WHERE id NOT IN ('T-001','T-002')")
            cur.execute("UPDATE tickets SET status='in_progress' WHERE id='T-001'")
            cur.execute("UPDATE tickets SET status='new' WHERE id='T-002'")
    finally:
        conn.close()


def episodic_write(user_id: str, summary: str, ticket_ids: list[str]) -> None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO episodic(user_id, summary, ticket_ids) VALUES (%s,%s,%s)",
                (user_id, summary, json.dumps(ticket_ids)),
            )
    finally:
        conn.close()


def episodic_read(user_id: str) -> list[dict[str, Any]]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT summary, ticket_ids, created_at FROM episodic WHERE user_id=%s ORDER BY id",
                (user_id,),
            )
            rows = cur.fetchall()
        out = []
        for r in rows:
            ids = r["ticket_ids"]
            if isinstance(ids, str):
                ids = json.loads(ids or "[]")
            out.append({"summary": r["summary"], "ticket_ids": ids, "created_at": str(r["created_at"])})
        return out
    finally:
        conn.close()


def episodic_clear() -> None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM episodic")
    finally:
        conn.close()


def _msg_from_row(r: dict[str, Any]) -> dict[str, Any]:
    src = r.get("sources")
    if isinstance(src, str):
        src = json.loads(src or "[]")
    return {
        "role": r["role"],
        "content": r["content"],
        "trace_id": r.get("trace_id") or "",
        "intent": r.get("intent") or "",
        "confidence": float(r.get("confidence") or 0),
        "sources": src or [],
        "blocked": bool(r.get("blocked")),
        "created_at": str(r.get("created_at", "")),
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
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO chat_sessions(session_id, user_id, title, updated_at, message_count)
                   VALUES (%s,%s,%s,%s,2)
                   ON DUPLICATE KEY UPDATE updated_at=VALUES(updated_at), message_count=message_count+2""",
                (session_id, user_id, title, updated),
            )
            for row in (user_row, assistant_row):
                cur.execute(
                    """INSERT INTO chat_messages
                       (session_id, role, content, trace_id, intent, confidence, sources, blocked, created_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
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
    finally:
        conn.close()


def conversation_list(limit: int = 50, user_id: str = "") -> list[dict[str, Any]]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute(
                    """SELECT session_id, user_id, title, updated_at, message_count
                       FROM chat_sessions WHERE user_id=%s ORDER BY updated_at DESC LIMIT %s""",
                    (user_id, limit),
                )
            else:
                cur.execute(
                    """SELECT session_id, user_id, title, updated_at, message_count
                       FROM chat_sessions ORDER BY updated_at DESC LIMIT %s""",
                    (limit,),
                )
            return list(cur.fetchall())
    finally:
        conn.close()


def conversation_get_messages(session_id: str) -> list[dict[str, Any]]:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT role, content, trace_id, intent, confidence, sources, blocked, created_at
                   FROM chat_messages WHERE session_id=%s ORDER BY id""",
                (session_id,),
            )
            return [_msg_from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()


def conversation_clear_all() -> None:
    init_db()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chat_messages")
            cur.execute("DELETE FROM chat_sessions")
    finally:
        conn.close()
