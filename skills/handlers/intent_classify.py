"""intent-classify — 规则引擎 + LLM 混合（2B 关键路径规则优先）."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from agent.identity import identity
from harness.runtime.context import HarnessContext

INTENT_LABELS: dict[str, str] = {
    "consult": "产品咨询",
    "ticket": "工单服务",
    "complaint": "投诉升级",
    "refund": "退款申请",
    "chitchat": "闲聊",
    "compliance": "合规",
    "crm": "客户查询",
    "unknown": "未识别",
}

CLARIFY_FALLBACK = identity.template("clarify")

_TICKET_UPDATE = re.compile(r"(更新|关闭|修改).*T-\d+|T-\d+.*(更新|关闭|优先级)", re.I)
_TICKET_QUERY = re.compile(
    r"(查|查询|查看|进度|处理到哪|状态|T-\d+|"
    r"查看工单|我的工单|工单列表|有哪些工单|"
    r"工单.*(哪|进度|状态|列表))",
    re.I,
)
_CRM = re.compile(r"(查客户|客户).*(C-\d+)|C-\d+", re.I)
_TICKET_CREATE = re.compile(
    r"(报修|宕机|无法启动|新建工单|创建工单|服务器.*(宕|挂)|设备.*(坏|故障)|网络异常|无法访问)",
    re.I,
)
_REFUND = re.compile(r"退款|退钱|我要退款", re.I)
_COMPLAINT = re.compile(r"投诉|太差|生气|没解决|三次|找经理", re.I)
_CONSULT = re.compile(
    r"(企业版|专业版|套餐|功能|发票|密码|SLA|如何|区别|包含哪些|忘记密码|怎么办)",
    re.I,
)
_CHITCHAT = re.compile(r"(天气|你好|您好|在吗|哈哈)", re.I)
_AMBIGUOUS = re.compile(r"^(嗯|啊|哦|帮我看看|看看)$|^(hi|hello)$", re.I)
_COMPLIANCE = re.compile(r"(绕过|违规|审核流程)", re.I)

# 2B 确定性：规则高置信时覆盖 LLM 误判
_RULE_OVERRIDE_INTENTS = frozenset({"ticket", "refund", "compliance", "complaint"})


@dataclass
class IntentResult:
    intent: str
    confidence: float
    needs_clarify: bool
    ticket_mode: str = ""

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "needs_clarify": self.needs_clarify,
            "ticket_mode": self.ticket_mode,
        }


def _classify_rules(text: str) -> IntentResult:
    if not text.strip():
        return IntentResult("unknown", 0.0, True)

    if _AMBIGUOUS.search(text) or (len(text.strip()) == 1):
        return IntentResult("unknown", 0.35, True)

    if _COMPLIANCE.search(text):
        return IntentResult("compliance", 0.9, False)

    if _CRM.search(text):
        return IntentResult("crm", 0.88, False)

    if "生气" in text and "订单" in text and "投诉" not in text:
        return IntentResult("complaint", 0.85, False)

    if _REFUND.search(text) and re.search(r"T-\d+", text, re.I):
        return IntentResult("ticket", 0.88, False, ticket_mode="query")

    if _REFUND.search(text):
        return IntentResult("refund", 0.93, False, ticket_mode="create")

    if _COMPLAINT.search(text):
        return IntentResult("complaint", 0.9, False)

    if _CHITCHAT.search(text):
        return IntentResult("chitchat", 0.85, False)

    if _TICKET_UPDATE.search(text):
        return IntentResult("ticket", 0.9, False, ticket_mode="update")

    if _TICKET_QUERY.search(text):
        return IntentResult("ticket", 0.91, False, ticket_mode="query")

    if _TICKET_CREATE.search(text):
        return IntentResult("ticket", 0.9, False, ticket_mode="create")

    if _CONSULT.search(text):
        return IntentResult("consult", 0.88, False)

    if "工单" in text:
        return IntentResult("ticket", 0.72, False, ticket_mode="query")

    return IntentResult("unknown", 0.4, True)


def _llm_allowed() -> bool:
    if os.getenv("EVAL_HARNESS", "").lower() in ("1", "true", "yes"):
        return False
    try:
        from backend.llm.adapter import llm

        return llm.enabled()
    except Exception:
        return False


def _merge_llm_and_rules(llm_out: dict, rule: IntentResult) -> IntentResult:
    llm_result = IntentResult(
        llm_out.get("intent", "unknown"),
        float(llm_out.get("confidence", 0.8)),
        bool(llm_out.get("needs_clarify", False)),
        ticket_mode=str(llm_out.get("ticket_mode", "")),
    )
    if (
        rule.confidence >= 0.88
        and rule.intent in _RULE_OVERRIDE_INTENTS
        and llm_result.intent != rule.intent
    ):
        return rule
    if rule.intent == "ticket" and rule.confidence >= 0.9 and llm_result.intent != "ticket":
        return rule
    if not llm_result.ticket_mode and rule.ticket_mode:
        llm_result.ticket_mode = rule.ticket_mode
    return llm_result


def classify_message(message: str) -> IntentResult:
    text = message.strip()
    rule = _classify_rules(text)

    if not _llm_allowed():
        return rule

    try:
        from backend.llm.adapter import llm

        llm_out = llm.classify_intent_json(text)
        if llm_out and llm_out.get("intent"):
            return _merge_llm_and_rules(llm_out, rule)
    except Exception:
        pass

    return rule


def classify_intent(ctx: HarnessContext) -> HarnessContext:
    result = classify_message(ctx.message)
    ctx.memory_context["intent_result"] = result.to_dict()
    ctx.memory_context["intent"] = result.intent
    ctx.memory_context["confidence"] = result.confidence
    return ctx
