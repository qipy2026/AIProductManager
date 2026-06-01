"""Memory Router — 按 Skill.memory_deps 注入."""

from __future__ import annotations

from backend.config import settings
from memory.stores.episodic import EpisodicMemoryStore
from memory.stores.profile import ProfileMemoryStore
from memory.stores.semantic import SemanticMemoryStore
from memory.stores.working import WorkingMemoryStore


def _build_semantic_store():
    if settings.semantic_backend == "chroma":
        try:
            from memory.stores.semantic_chroma import ChromaSemanticStore

            return ChromaSemanticStore()
        except Exception:
            pass
    return SemanticMemoryStore()


_semantic_store_instance = None


def get_semantic_store():
    global _semantic_store_instance
    if _semantic_store_instance is None:
        _semantic_store_instance = _build_semantic_store()
    return _semantic_store_instance


def reset_semantic_store() -> None:
    global _semantic_store_instance
    _semantic_store_instance = None


# 全局单例（Demo；生产 SQLite + Chroma）
working_store = WorkingMemoryStore()
episodic_store = EpisodicMemoryStore()
profile_store = ProfileMemoryStore()
semantic_store = get_semantic_store()


class MemoryRouter:
    def __init__(
        self,
        working: WorkingMemoryStore | None = None,
        episodic: EpisodicMemoryStore | None = None,
        profile: ProfileMemoryStore | None = None,
        semantic: SemanticMemoryStore | None = None,
    ) -> None:
        self.working = working or working_store
        self.episodic = episodic or episodic_store
        self.profile = profile or profile_store
        self.semantic = semantic or semantic_store

    def inject(
        self,
        *,
        session_id: str,
        user_id: str,
        message: str,
        memory_deps: list[str],
        intent: str = "",
    ) -> tuple[dict, list[str]]:
        """返回 memory_context 片段 + 注入层列表."""
        ctx: dict = {}
        injected: list[str] = []

        if "working" in memory_deps:
            wm = self.working.get(session_id)
            wm.append("user", message)
            ctx["working"] = wm.to_context()
            injected.append("working")

        if "profile" in memory_deps and user_id:
            prof = self.profile.get(user_id)
            if prof:
                ctx["profile"] = prof.to_context()
                injected.append("profile")

        # 纯知识问答不注入 episodic（UT-M-007）
        if "episodic" in memory_deps and user_id and intent not in ("consult",):
            eps = self.episodic.read(user_id)
            if eps:
                ctx["episodic"] = eps[-1]
                injected.append("episodic")

        if "semantic" in memory_deps:
            ctx["semantic_hits"] = get_semantic_store().search(message)
            injected.append("semantic")

        return ctx, injected

    def resolve_conflict(self, profile: dict, episodic: dict) -> dict:
        """Profile 优先于 Episodic（UT-M-008）."""
        merged = dict(episodic)
        merged.update(profile)
        return merged
