"""工单查询 API — 运营/前端查看."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.tools.ticket_mock import ticket_api

router = APIRouter()


@router.get("/tickets")
def list_tickets() -> dict:
    items = ticket_api.list_all()
    return {
        "items": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at,
            }
            for t in items
        ],
        "total": len(items),
    }


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict:
    t = ticket_api.get(ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"工单 {ticket_id} 不存在")
    return {
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "priority": t.priority,
        "created_at": t.created_at,
    }
