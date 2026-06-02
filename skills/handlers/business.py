"""业务 Skill Handlers — M2."""

from __future__ import annotations

import re

from agent.identity import identity
from backend.tools.ticket_mock import ticket_api
from harness.runtime.context import HarnessContext

TICKET_CREATE_FALLBACK = identity.template("ticket_create_fallback")
TICKET_QUERY_FALLBACK = identity.template("ticket_query_fallback")


def knowledge_retrieve(ctx: HarnessContext) -> HarnessContext:
    from memory.router.router import get_semantic_store

    hits = ctx.memory_context.get("semantic_hits") or get_semantic_store().search(ctx.message)
    ctx.memory_context["chunks"] = hits
    ctx.memory_context["sources"] = [
        {"id": h["id"], "title": h["title"], "url": h.get("url", "")} for h in hits
    ]
    ctx.memory_context["require_source"] = True
    return ctx


def answer_compose(ctx: HarnessContext) -> HarnessContext:
    chunks = ctx.memory_context.get("chunks", [])
    sources = ctx.memory_context.get("sources", [])
    if not chunks:
        ctx.response = identity.template("no_kb_hit")
        return ctx

    from backend.llm.adapter import llm

    if llm.enabled():
        composed = llm.compose_answer(ctx.message, chunks, sources=sources)
        if composed:
            ctx.response = composed
            ctx.memory_context["source_refs"] = sources
            return ctx

    main = chunks[0]
    refs = " ".join(f"[{i+1}]" for i in range(len(sources)))
    ctx.response = (
        f"{main['content']}\n\n"
        f"📎 来源：{main['title']} {refs}"
    )
    ctx.memory_context["source_refs"] = sources
    return ctx


_TICKET_LIST = re.compile(r"查看工单|我的工单|工单列表|有哪些工单|查看我的工单", re.I)


def ticket_query(ctx: HarnessContext) -> HarnessContext:
    msg = ctx.message
    tid = ticket_api.extract_ticket_id(msg)
    if not tid:
        ep = ctx.memory_context.get("episodic") or {}
        ids = ep.get("ticket_ids") if isinstance(ep, dict) else []
        if ids:
            tid = ids[0]
    if not tid and _TICKET_LIST.search(msg):
        items = ticket_api.list_all()
        if not items:
            ctx.response = "当前没有工单记录。"
            return ctx
        lines = [f"- {t.id} [{t.status}] {t.title}" for t in items]
        ctx.response = f"{identity.template('ticket_list_intro')}\n" + "\n".join(lines)
        ctx.memory_context["ticket_list"] = [t.id for t in items]
        return ctx
    if not tid:
        ctx.response = TICKET_QUERY_FALLBACK
        ctx.memory_context["fallback"] = "ask-ticket-id"
        return ctx
    ticket = ticket_api.get(tid)
    if not ticket:
        ctx.response = f"未找到工单 {tid}，请核对工单号。"
        return ctx
    ctx.response = f"工单 {ticket.id} 当前状态：「{ticket.status}」，标题：{ticket.title}。"
    ctx.memory_context["ticket_id"] = ticket.id
    return ctx


def ticket_create(ctx: HarnessContext) -> HarnessContext:
    msg = ctx.message
    if re.match(r"^(我要报修|报修)$", msg.strip()):
        ctx.response = TICKET_CREATE_FALLBACK
        ctx.memory_context["fallback"] = "ticket-template"
        return ctx
    title = msg
    for kw in ("我要报修", "请尽快处理", "，", "。"):
        title = title.replace(kw, "")
    title = title.strip() or "用户报修"
    priority = "urgent" if any(k in msg for k in ("宕机", "紧急", "尽快")) else "normal"
    ticket = ticket_api.create(title=title[:100], priority=priority)
    ctx.response = f"已为您创建工单 {ticket.id}，当前状态：{ticket.status}。我们会尽快处理。"
    ctx.memory_context["ticket_id"] = ticket.id
    return ctx


def escalation_judge(ctx: HarnessContext) -> HarnessContext:
    ctx.memory_context["escalation_recommended"] = True
    return ctx


def human_handoff(ctx: HarnessContext) -> HarnessContext:
    ctx.response = identity.template("human_handoff")
    ctx.memory_context["handoff"] = True
    return ctx


def sentiment_analyze(ctx: HarnessContext) -> HarnessContext:
    score = 0.8 if any(k in ctx.message for k in ("太差", "生气", "投诉")) else 0.5
    ctx.memory_context["sentiment_score"] = score
    return ctx


def ticket_update(ctx: HarnessContext) -> HarnessContext:
    tid = ticket_api.extract_ticket_id(ctx.message)
    if not tid:
        ctx.response = "请提供要更新的工单号（如 T-002）。"
        ctx.memory_context["fallback"] = "ask-ticket-id"
        return ctx
    ticket = ticket_api.get(tid)
    if not ticket:
        ctx.response = f"未找到工单 {tid}。"
        return ctx
    if "关闭" in ctx.message:
        ticket_api.update(tid, status="closed")
        ctx.response = f"工单 {tid} 已关闭。"
    elif "优先级" in ctx.message or "更新" in ctx.message:
        ticket_api.update(tid, status="in_progress")
        ctx.response = f"工单 {tid} 已更新，当前状态：in_progress。"
    else:
        ctx.response = f"工单 {tid} 当前状态：{ticket.status}。"
    ctx.memory_context["ticket_id"] = tid
    return ctx


def crm_lookup(ctx: HarnessContext) -> HarnessContext:
    m = re.search(r"C-\d+", ctx.message, re.I)
    cid = m.group(0).upper() if m else ""
    prof = ctx.memory_context.get("profile") or {}
    tier = prof.get("tier", "standard")
    if cid == "C-1001" or tier == "VIP":
        ctx.response = f"客户 {cid or 'C-1001'}：VIP 企业版客户，套餐 SLA 99.95%。"
    else:
        ctx.response = f"客户 {cid or '未知'}：标准版客户。"
    ctx.memory_context["customer_id"] = cid
    return ctx


def compliance_check(ctx: HarnessContext) -> HarnessContext:
    ctx.response = identity.template("compliance_blocked")
    ctx.memory_context["compliance_blocked"] = True
    return ctx


def agent_route(ctx: HarnessContext) -> HarnessContext:
    ctx.memory_context["routed_agent"] = "router-agent"
    return ctx
