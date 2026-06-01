"""知识库 API — 来源文档查看."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

KB_PATH = Path(__file__).resolve().parents[2] / "knowledge-base" / "faq.json"


def _load_kb() -> list[dict]:
    if not KB_PATH.exists():
        return []
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


@router.get("/kb")
def list_kb() -> dict:
    docs = _load_kb()
    return {
        "items": [
            {"id": d["id"], "title": d["title"], "url": d.get("url", f"/kb/{d['id']}")}
            for d in docs
        ]
    }


@router.get("/kb/{doc_id}")
def get_kb_doc(doc_id: str) -> dict:
    for doc in _load_kb():
        if doc["id"] == doc_id:
            return {
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "keywords": doc.get("keywords", []),
                "url": doc.get("url", f"/kb/{doc['id']}"),
            }
    raise HTTPException(status_code=404, detail=f"document not found: {doc_id}")
