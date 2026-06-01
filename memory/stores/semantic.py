"""Semantic Memory — 知识库检索（M2 Mock 关键词）."""

from __future__ import annotations

import json
from pathlib import Path

KB_PATH = Path(__file__).resolve().parents[2] / "knowledge-base" / "faq.json"


class SemanticMemoryStore:
    def __init__(self, kb_path: Path | None = None) -> None:
        self.kb_path = kb_path or KB_PATH
        self._docs: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.kb_path.exists():
            self._docs = json.loads(self.kb_path.read_text(encoding="utf-8"))

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        q = query.lower()
        scored: list[tuple[int, dict]] = []
        for doc in self._docs:
            text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
            score = sum(1 for kw in doc.get("keywords", []) if kw.lower() in q)
            if any(w in text for w in q.split() if len(w) > 1):
                score += 1
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [
            {
                "id": d["id"],
                "title": d["title"],
                "content": d["content"],
                "url": d.get("url", ""),
            }
            for _, d in scored[:top_k]
        ]
