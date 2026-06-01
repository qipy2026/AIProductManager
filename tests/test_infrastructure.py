"""LangGraph / SQLite / LLM 基础设施测试."""

import os

import pytest


def test_langgraph_build():
    os.environ["USE_LANGGRAPH"] = "1"
    from agent.graph import build_langgraph_agent

    graph = build_langgraph_agent()
    assert graph is not None


def test_langgraph_run_consult():
    os.environ["USE_LANGGRAPH"] = "1"
    from agent.graph import run_langgraph

    ctx = run_langgraph("企业版套餐功能", session_id="lg-1")
    assert ctx.response
    assert "intent-classify" in ctx.trace.skills_invoked


def test_sqlite_trace_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOPS_STORAGE", "sqlite")
    monkeypatch.setenv("AGENTOPS_DB", str(tmp_path / "test.db"))
    from backend.db import sqlite_store
    from harness.runtime.context import HarnessTrace
    from harness.runtime import trace_store

    sqlite_store.init_db()
    tr = HarnessTrace(trace_id="t-sqlite-1")
    trace_store.save_trace(tr, extras={"response": "hi", "intent": "chitchat"})
    got = trace_store.get_trace("t-sqlite-1")
    assert got and got["response"] == "hi"


def test_llm_mock_returns_none():
    from backend.llm.adapter import llm

    assert llm.classify_intent_json("你好") is None


def test_badcase_api(tmp_path, monkeypatch):
    monkeypatch.setenv("OPS_DB", "sqlite")
    monkeypatch.setenv("AGENTOPS_DB", str(tmp_path / "ops_test.db"))

    from importlib import reload
    import backend.config as cfg
    import backend.db.store as store_mod

    reload(cfg)
    reload(store_mod)

    from fastapi.testclient import TestClient
    from backend.main import app

    c = TestClient(app)
    r = c.post("/api/ops/badcases", json={"attribution": "skill", "note": "test"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
