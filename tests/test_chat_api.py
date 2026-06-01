"""Chat API 集成测试 — M2 Orchestrator 全链路."""

from fastapi.testclient import TestClient

from backend.main import app
from backend.tools.ticket_mock import ticket_api
from harness.runtime.trace_store import clear_traces
from memory.router.router import working_store

client = TestClient(app)


def setup_function():
    clear_traces()
    ticket_api.clear()
    working_store.clear()


def test_chat_consult_with_sources():
    r = client.post(
        "/api/chat",
        json={"message": "企业版和专业版有什么区别？", "session_id": "m2-c1"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "consult"
    assert "knowledge-retrieve" in data["skills_invoked"]
    assert "answer-compose" in data["skills_invoked"]
    assert data["sources"]
    assert "企业版" in data["response"] or "专业版" in data["response"]


def test_chat_ticket_query_no_create():
    before = len(ticket_api._tickets)
    r = client.post(
        "/api/chat",
        json={"message": "查 T-001 进度", "session_id": "m2-q1"},
    )
    data = r.json()
    assert "ticket-query" in data["skills_invoked"]
    assert "ticket-create" not in data["skills_invoked"]
    assert len(ticket_api._tickets) == before


def test_chat_ticket_create():
    r = client.post(
        "/api/chat",
        json={"message": "服务器宕机请处理", "session_id": "m2-t1"},
    )
    data = r.json()
    assert "ticket-create" in data["skills_invoked"]
    assert "T-" in data["response"]


def test_trace_api_after_chat():
    r = client.post("/api/chat", json={"message": "我要退款", "session_id": "s"})
    trace_id = r.json()["trace_id"]
    tr = client.get(f"/api/traces/{trace_id}")
    assert tr.status_code == 200
    assert "intent-classify" in tr.json()["skills_invoked"]


def test_trace_not_found():
    r = client.get("/api/traces/nonexistent-id")
    assert r.status_code == 404
