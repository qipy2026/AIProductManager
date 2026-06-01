"""Sessions API — 历史对话列表与续聊."""

from fastapi.testclient import TestClient

from backend.db.conversations import clear_all, get_messages, list_sessions
from backend.main import app
from harness.runtime.trace_store import clear_traces
from memory.router.router import working_store

client = TestClient(app)


def setup_function():
    clear_traces()
    clear_all()
    working_store.clear()


def test_sessions_empty():
    r = client.get("/api/sessions")
    assert r.status_code == 200
    assert r.json()["sessions"] == []


def test_chat_persists_session_history():
    sid = "sess-hist-1"
    r = client.post("/api/chat", json={"message": "企业版和专业版区别", "session_id": sid})
    assert r.status_code == 200
    assert r.json()["session_id"] == sid

    sessions = list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == sid
    assert "企业版" in sessions[0]["title"] or "专业版" in sessions[0]["title"]

    msgs = get_messages(sid)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_list_and_get_session_api():
    sid = "sess-hist-2"
    client.post("/api/chat", json={"message": "查 T-001 进度", "session_id": sid})

    r = client.get("/api/sessions")
    ids = [s["session_id"] for s in r.json()["sessions"]]
    assert sid in ids

    detail = client.get(f"/api/sessions/{sid}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["session_id"] == sid
    assert len(body["messages"]) == 2
    assert body["messages"][0]["content"] == "查 T-001 进度"


def test_continue_session_same_id():
    sid = "sess-continue"
    client.post("/api/chat", json={"message": "你好", "session_id": sid})
    r2 = client.post("/api/chat", json={"message": "帮我查工单", "session_id": sid})
    assert r2.status_code == 200
    assert r2.json()["session_id"] == sid
    assert len(get_messages(sid)) == 4


def test_session_not_found():
    r = client.get("/api/sessions/does-not-exist")
    assert r.status_code == 404


def test_create_session_endpoint():
    r = client.post("/api/sessions")
    assert r.status_code == 200
    assert r.json()["session_id"].startswith("sess-")
