"""Agent Identity 加载与模板一致性."""

from agent.identity import identity
from skills.handlers.intent_classify import CLARIFY_FALLBACK
from skills.handlers.business import TICKET_CREATE_FALLBACK, TICKET_QUERY_FALLBACK


class TestAgentIdentity:
    def test_docs_exist(self):
        for name in ("AGENT", "SOUL", "MEMORY", "TOOLS"):
            text = identity.doc(name)
            assert len(text) > 100
            assert name in text or "Harness" in text or "智服通" in text

    def test_version(self):
        assert identity.version() == "1.0.0"

    def test_system_prompts(self):
        for role in ("classify", "compose", "chat"):
            prompt = identity.system_prompt(role)
            assert "智服通" in prompt or "意图" in prompt or "JSON" in prompt
            assert "B2B" not in prompt

    def test_templates_match_legacy_constants(self):
        assert CLARIFY_FALLBACK == identity.template("clarify")
        assert TICKET_CREATE_FALLBACK == identity.template("ticket_create_fallback")
        assert TICKET_QUERY_FALLBACK == identity.template("ticket_query_fallback")

    def test_guardrail_templates(self):
        assert "不允许" in identity.template("guardrail_injection")
        assert "敏感" in identity.template("guardrail_sensitive")

    def test_agent_docs_no_b2b_persona(self):
        """B2B 仅用于产品/背景描述，不得出现在客服人设语境."""
        bad_patterns = ("B2B 客服", "B2B 智能客服助手", "B2B 助手")
        for name in ("AGENT", "SOUL", "MEMORY", "TOOLS"):
            text = identity.doc(name)
            for pat in bad_patterns:
                assert pat not in text, f"{name}.md contains {pat!r}"

    def test_metadata(self):
        meta = identity.metadata()
        assert meta["identity_version"] == "1.0.0"
        assert "SOUL.md" in meta["soul_doc"]
