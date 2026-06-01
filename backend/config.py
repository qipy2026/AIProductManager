"""应用配置 — 环境变量驱动."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _resolve_llm_mode() -> str:
    explicit = os.getenv("LLM_MODE", "").strip().lower()
    if explicit:
        return explicit
    if os.getenv("LLM_API_KEY") or os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "mock"


from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    storage: str = os.getenv("AGENTOPS_STORAGE", "memory")  # memory | sqlite | mysql
    ops_db: str = os.getenv("OPS_DB", "sqlite")  # sqlite | mysql | none（关闭运营持久化）
    db_path: str = os.getenv("AGENTOPS_DB", "data/agentops.db")
    chroma_path: str = os.getenv("AGENTOPS_CHROMA", "data/chroma")
    semantic_backend: str = os.getenv("SEMANTIC_BACKEND", "keyword")
    llm_mode: str = _resolve_llm_mode()  # mock | openai
    llm_api_key: str = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "") or "ollama"
    llm_base_url: str = os.getenv("LLM_BASE_URL") or os.getenv(
        "OPENAI_BASE_URL", "https://api.openai.com/v1"
    )
    llm_model: str = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    use_langgraph: bool = os.getenv("USE_LANGGRAPH", "0") == "1"
    mysql_host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "agentops")


settings = Settings()
