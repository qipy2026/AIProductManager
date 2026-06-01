"""OpenAI 兼容 LLM 适配器 — mock / openai 双模式."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.config import settings


class LLMAdapter:
    """统一 LLM 调用；Eval/CI 默认 mock，配置 LLM_* 或 LLM_MODE=openai 启用."""

    @staticmethod
    def enabled() -> bool:
        return settings.llm_mode not in ("mock", "off", "none", "")

    def complete(self, prompt: str, *, system: str = "", temperature: float = 0.0) -> str:
        if not self.enabled():
            return ""
        try:
            return self._openai_complete(prompt, system=system, temperature=temperature)
        except Exception:
            return ""

    def classify_intent_json(self, message: str) -> dict[str, Any] | None:
        """LLM 意图识别；mock 模式返回 None 由规则引擎兜底."""
        sys_prompt = (
            "你是意图分类器。仅输出 JSON："
            '{"intent":"consult|ticket|complaint|refund|chitchat|compliance|crm|unknown",'
            '"confidence":0.0-1.0,"needs_clarify":bool,"ticket_mode":"query|create|update|"}'
        )
        raw = self.complete(f"用户消息：{message}", system=sys_prompt, temperature=0.0)
        if not raw:
            return None
        try:
            m = re.search(r"\{.*\}", raw, re.S)
            if m:
                return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
        return None

    def compose_answer(
        self,
        message: str,
        chunks: list[dict[str, Any]],
        *,
        sources: list[dict[str, Any]] | None = None,
    ) -> str:
        """基于检索片段生成带引用的客服回复."""
        if not chunks:
            return ""
        refs = sources or [
            {"title": c.get("title", ""), "id": c.get("id", "")} for c in chunks
        ]
        ctx_lines = "\n".join(
            f"[{i + 1}] {c.get('title', '知识')}: {c.get('content', '')}" for i, c in enumerate(chunks)
        )
        src_line = " · ".join(f"{s.get('title', '')}" for s in refs if s.get("title"))
        sys_prompt = (
            "你是智服通 B2B 智能客服助手。"
            "仅根据提供的知识库片段回答，不要编造片段中不存在的内容。"
            "回答末尾用一行标注来源，格式：📎 来源：文档名"
        )
        prompt = f"用户问题：{message}\n\n知识库片段：\n{ctx_lines}\n\n请用中文简洁回答。"
        raw = self.complete(prompt, system=sys_prompt, temperature=0.3)
        if not raw:
            return ""
        if "📎" not in raw and src_line:
            raw = f"{raw.rstrip()}\n\n📎 来源：{src_line}"
        return raw.strip()

    def chat_reply(self, message: str, *, history: str = "") -> str:
        """通用对话回复（闲聊/兜底）."""
        sys_prompt = (
            "你是智服通 B2B 智能客服助手，可帮用户咨询产品、查询或创建工单。"
            "回答简洁友好，使用中文。"
        )
        prompt = message
        if history:
            prompt = f"对话历史：\n{history}\n\n用户：{message}"
        return self.complete(prompt, system=sys_prompt, temperature=0.5)

    def _openai_complete(self, prompt: str, *, system: str, temperature: float) -> str:
        try:
            import httpx
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("openai package required when LLM is enabled") from e

        # 本地 Ollama 需绕过系统 HTTP 代理，否则 Windows 上易 502
        bypass_proxy = "localhost" in settings.llm_base_url or "127.0.0.1" in settings.llm_base_url
        http_client = httpx.Client(trust_env=not bypass_proxy, timeout=180.0)
        client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            http_client=http_client,
        )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            resp = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""
        finally:
            http_client.close()


llm = LLMAdapter()
