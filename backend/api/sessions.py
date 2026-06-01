"""对话会话 API — 历史记录与续聊."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.db import conversations

router = APIRouter()


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionItem(BaseModel):
    session_id: str
    user_id: str = ""
    title: str = ""
    updated_at: str = ""
    message_count: int = 0


class MessageItem(BaseModel):
    role: str
    content: str
    trace_id: str = ""
    intent: str = ""
    confidence: float = 0.0
    sources: list = Field(default_factory=list)
    blocked: bool = False
    created_at: str = ""


class SessionDetail(BaseModel):
    session_id: str
    title: str = ""
    messages: list[MessageItem]


@router.get("/sessions")
def list_sessions(user_id: str = "", limit: int = 50) -> dict:
    items = conversations.list_sessions(limit=min(limit, 100), user_id=user_id)
    return {"sessions": items}


@router.post("/sessions", response_model=SessionCreateResponse)
def create_session(user_id: str = "") -> SessionCreateResponse:
    sid = f"sess-{uuid.uuid4().hex[:12]}"
    return SessionCreateResponse(session_id=sid)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: str) -> SessionDetail:
    msgs = conversations.get_messages(session_id)
    if not msgs:
        # 允许空会话（刚创建尚未发消息）
        sessions = conversations.list_sessions(limit=200)
        meta = next((s for s in sessions if s["session_id"] == session_id), None)
        if not meta:
            raise HTTPException(status_code=404, detail=f"session not found: {session_id}")
        return SessionDetail(session_id=session_id, title=meta.get("title", ""), messages=[])
    title = ""
    for s in conversations.list_sessions(limit=200):
        if s["session_id"] == session_id:
            title = s.get("title", "")
            break
    return SessionDetail(
        session_id=session_id,
        title=title,
        messages=[MessageItem(**m) for m in msgs],
    )
