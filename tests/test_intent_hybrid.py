"""意图混合分类 — 规则覆盖 LLM 误判."""

from skills.handlers.intent_classify import _classify_rules, classify_message


def test_refund_rules():
    r = _classify_rules("我要退款")
    assert r.intent == "refund"
    assert r.ticket_mode == "create"


def test_view_ticket_rules():
    r = _classify_rules("查看工单 T-001")
    assert r.intent == "ticket"
    assert r.ticket_mode == "query"


def test_server_down_rules():
    r = _classify_rules("服务器宕机")
    assert r.intent == "ticket"
    assert r.ticket_mode == "create"


def test_ticket_list_phrase():
    r = _classify_rules("查看我的工单列表")
    assert r.intent == "ticket"
    assert r.ticket_mode == "query"
