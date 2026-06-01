"""Trace 查询 API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from harness.runtime.trace_store import get_trace

router = APIRouter()


@router.get("/traces/{trace_id}")
def get_trace_by_id(trace_id: str) -> dict:
    data = get_trace(trace_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"trace not found: {trace_id}")
    duration_ms = sum(s.get("duration_ms", 0) for s in data.get("steps", []))
    return {
        "trace_id": data["trace_id"],
        "session_id": data.get("session_id", ""),
        "user_id": data.get("user_id", ""),
        "started_at": data.get("started_at", ""),
        "duration_ms": round(duration_ms, 2),
        "skills_invoked": data.get("skills_invoked", []),
        "memory_injected": data.get("memory_injected", []),
        "attribution": data.get("attribution", ""),
        "steps": data.get("steps", []),
    }
