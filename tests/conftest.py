"""pytest 全局配置 — 测试使用内存后端保证隔离."""

from __future__ import annotations

import os

os.environ["AGENTOPS_STORAGE"] = "memory"
os.environ["SEMANTIC_BACKEND"] = "keyword"
os.environ["LLM_MODE"] = "mock"
os.environ["OPS_DB"] = "none"
os.environ["USE_LANGGRAPH"] = "0"

import pytest


@pytest.fixture(autouse=True)
def _reset_runtime_state():
    """每条用例前清空进程内状态，避免对话历史/Trace 串测."""
    from backend.db.conversations import clear_all
    from backend.tools.ticket_mock import ticket_api
    from harness.runtime.trace_store import clear_traces
    from memory.router.router import working_store

    clear_traces()
    clear_all()
    working_store.clear()
    ticket_api.clear()
    yield
