"""Chroma 向量语义检索 — FAQ 持久化索引."""

from __future__ import annotations

import json
from pathlib import Path

from backend.config import settings

KB_PATH = Path(__file__).resolve().parents[2] / "knowledge-base" / "faq.json"


class ChromaSemanticStore:
    def __init__(self, kb_path: Path | None = None) -> None:
        self.kb_path = kb_path or KB_PATH
        self._docs: list[dict] = []
        self._collection = None
        self._load_docs()
        self._init_chroma()

    def _load_docs(self) -> None:
        if self.kb_path.exists():
            self._docs = json.loads(self.kb_path.read_text(encoding="utf-8"))

    def _init_chroma(self) -> None:
        try:
            import chromadb
        except ImportError:
            return
        path = Path(settings.chroma_path)
        path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(path))
        self._collection = client.get_or_create_collection(
            name="faq",
            metadata={"hnsw:space": "cosine"},
        )
        if self._collection.count() == 0 and self._docs:
            ids = [d["id"] for d in self._docs]
            documents = [f"{d['title']} {d['content']}" for d in self._docs]
            metadatas = [{"title": d["title"], "url": d.get("url", "")} for d in self._docs]
            self._collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self._collection is not None:
            try:
                res = self._collection.query(query_texts=[query], n_results=top_k)
                ids = (res.get("ids") or [[]])[0]
                docs = (res.get("documents") or [[]])[0]
                metas = (res.get("metadatas") or [[]])[0]
                dists = (res.get("distances") or [[]])[0]
                hits: list[dict] = []
                for i, doc_id in enumerate(ids):
                    # cosine distance > 0.85 视为无相关命中
                    if dists and i < len(dists) and dists[i] > 0.85:
                        continue
                    full = next((d for d in self._docs if d["id"] == doc_id), None)
                    if full:
                        hits.append(
                            {
                                "id": doc_id,
                                "title": full["title"],
                                "content": full["content"],
                                "url": full.get("url", ""),
                            }
                        )
                    elif docs and i < len(docs):
                        meta = metas[i] if metas and i < len(metas) else {}
                        hits.append(
                            {
                                "id": doc_id,
                                "title": meta.get("title", doc_id),
                                "content": docs[i],
                                "url": meta.get("url", ""),
                            }
                        )
                if hits:
                    return hits
            except Exception:
                pass
        return self._keyword_fallback(query, top_k)

    def _keyword_fallback(self, query: str, top_k: int) -> list[dict]:
        from memory.stores.semantic import SemanticMemoryStore

        return SemanticMemoryStore(self.kb_path).search(query, top_k)
