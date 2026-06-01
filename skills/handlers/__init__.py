"""Skill 处理器注册表."""

from skills.handlers.business import (
    agent_route,
    answer_compose,
    compliance_check,
    crm_lookup,
    escalation_judge,
    human_handoff,
    knowledge_retrieve,
    sentiment_analyze,
    ticket_create,
    ticket_query,
    ticket_update,
)
from skills.handlers.intent_classify import classify_intent

HANDLERS: dict[str, object] = {
    "intent-classify": classify_intent,
    "agent-route": agent_route,
    "knowledge-retrieve": knowledge_retrieve,
    "answer-compose": answer_compose,
    "ticket-create": ticket_create,
    "ticket-query": ticket_query,
    "ticket-update": ticket_update,
    "sentiment-analyze": sentiment_analyze,
    "escalation-judge": escalation_judge,
    "human-handoff": human_handoff,
    "crm-lookup": crm_lookup,
    "compliance-check": compliance_check,
}
