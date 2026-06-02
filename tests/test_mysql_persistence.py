"""MySQL 持久化集成测试 — 无 MySQL 时自动 skip."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_TESTS", "").lower() not in ("1", "true", "yes"),
    reason="设置 RUN_MYSQL_TESTS=1 且 MySQL 可用时运行",
)


@pytest.fixture
def mysql_env(monkeypatch):
    monkeypatch.setenv("OPS_DB", "mysql")
    monkeypatch.setenv("MYSQL_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
    monkeypatch.setenv("MYSQL_PORT", os.getenv("MYSQL_PORT", "3306"))
    monkeypatch.setenv("MYSQL_USER", os.getenv("MYSQL_USER", "agentops"))
    monkeypatch.setenv("MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "Agentops@2026!"))
    monkeypatch.setenv("MYSQL_DATABASE", os.getenv("MYSQL_DATABASE", "agentops"))


def _reload_app():
    import importlib

    import backend.config as cfg
    import backend.db.store as store_mod
    import backend.main as main_mod

    importlib.reload(cfg)
    importlib.reload(store_mod)
    importlib.reload(main_mod)
    return main_mod.app


def test_mysql_trace_roundtrip(mysql_env):
    from backend.db import mysql_store

    mysql_store.init_db()
    tid = "pytest-mysql-trace"
    payload = {"trace_id": tid, "session_id": "pytest", "response": "harness-ok"}
    mysql_store.trace_save(tid, payload)
    got = mysql_store.trace_get(tid)
    assert got is not None
    assert got["trace_id"] == tid
    assert got["response"] == "harness-ok"


def test_harness_chat_persists_to_mysql(mysql_env):
    from fastapi.testclient import TestClient

    from backend.db import mysql_store

    app = _reload_app()
    mysql_store.init_db()
    client = TestClient(app)
    r = client.post(
        "/api/chat",
        json={"message": "查 T-001 进度", "session_id": "pytest-mysql-chat"},
    )
    assert r.status_code == 200
    data = r.json()
    tid = data["trace_id"]
    assert mysql_store.trace_get(tid) is not None
    msgs = mysql_store.conversation_get_messages("pytest-mysql-chat")
    assert len(msgs) >= 2
