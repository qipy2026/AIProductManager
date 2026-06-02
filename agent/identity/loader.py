"""Agent Identity 加载器 — SOUL / AGENT 文档 + templates.yaml 运行时注入."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

AGENT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = AGENT_ROOT / "templates.yaml"


class AgentIdentity:
    """Harness Agent 身份：Markdown 文档 + 可执行模板."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or AGENT_ROOT
        self._templates: dict[str, Any] | None = None

    def _load_templates(self) -> dict[str, Any]:
        if self._templates is None:
            with (self.root / "templates.yaml").open(encoding="utf-8") as f:
                self._templates = yaml.safe_load(f) or {}
        return self._templates

    def reload(self) -> None:
        """热加载（开发/测试用）."""
        self._templates = None
        self.doc.cache_clear()

    @lru_cache(maxsize=8)
    def doc(self, name: str) -> str:
        """加载 AGENT / SOUL / MEMORY / TOOLS Markdown."""
        path = self.root / f"{name.upper()}.md"
        if not path.exists():
            path = self.root / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Agent doc not found: {name}")
        return path.read_text(encoding="utf-8")

    def version(self) -> str:
        return str(self._load_templates().get("version", "0.0.0"))

    def system_prompt(self, role: str) -> str:
        """LLM system prompt：classify | compose | chat."""
        data = self._load_templates().get("system", {})
        key = role.strip().lower()
        text = data.get(key, "")
        if not text:
            raise KeyError(f"Unknown system prompt role: {role}")
        return str(text).strip()

    def template(self, key: str) -> str:
        """固定回复模板：clarify / human_handoff / ..."""
        data = self._load_templates().get("responses", {})
        if key not in data:
            raise KeyError(f"Unknown response template: {key}")
        return str(data[key]).strip()

    def metadata(self) -> dict[str, str]:
        return {
            "identity_version": self.version(),
            "soul_doc": "agent/SOUL.md",
            "agent_doc": "agent/AGENT.md",
        }


identity = AgentIdentity()

# 便捷别名（兼容旧常量名）
def clarify_fallback() -> str:
    return identity.template("clarify")


def chitchat_greeting() -> str:
    return identity.template("chitchat_greeting")
