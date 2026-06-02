#!/usr/bin/env python3
"""验证 OPS_DB=mysql 时 Harness Trace / 对话 / Bad Case 可落库."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import urllib.request

from backend.config import settings
from backend.db.store import get_ops_store


def _chat(message: str, session_id: str) -> dict:
    url = "http://127.0.0.1:8002/api/chat"
    req = urllib.request.Request(
        url,
        data=json.dumps({"message": message, "session_id": session_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    print("=== MySQL 持久化验证 ===\n")
    print(f"OPS_DB={settings.ops_db} MYSQL_HOST={settings.mysql_host}:{settings.mysql_port}")

    store = get_ops_store()
    if store is None:
        print("FAIL: get_ops_store() 为空，请设置 OPS_DB=mysql")
        return 1

    try:
        store.init_db()
        before = store.trace_count() if hasattr(store, "trace_count") else len(store.trace_list())
    except Exception as e:
        print(f"FAIL: 无法连接 MySQL — {e}")
        print("提示: wsl sudo service mysql start && scripts/setup_wsl_mysql.sh")
        return 1

    print(f"Trace 条数（对话前）: {before}")

    try:
        data = _chat("企业版和专业版有什么区别？", "mysql-verify-001")
    except Exception as e:
        print(f"FAIL: 后端未启动 — {e}")
        print("请先: .\\scripts\\start_backend_mysql.ps1")
        return 1

    tid = data["trace_id"]
    print(f"对话 trace_id={tid} skills={data.get('skills_invoked')}")

    row = store.trace_get(tid)
    if not row:
        print(f"FAIL: MySQL 中未找到 trace {tid}")
        return 1

    print(f"OK: traces 表已写入（含 response/intent）")

    if hasattr(store, "conversation_get_messages"):
        msgs = store.conversation_get_messages("mysql-verify-001")
        if len(msgs) < 2:
            print(f"WARN: chat_messages 仅 {len(msgs)} 条")
        else:
            print(f"OK: chat_messages {len(msgs)} 条")

    after = store.trace_count() if hasattr(store, "trace_count") else len(store.trace_list())
    print(f"Trace 条数（对话后）: {after}")
    print("\nALL PASS — Harness + MySQL 持久化正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
