"""运营统计 API."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.config import settings
from backend.db.store import get_ops_store
from harness.runtime.trace_store import get_trace, list_trace_ids
from skills.runtime.registry import SkillRegistry

router = APIRouter()

_trace_index: list[str] = []


def index_trace(trace_id: str) -> None:
    if trace_id not in _trace_index:
        _trace_index.append(trace_id)


class BadCaseCreate(BaseModel):
    trace_id: str = ""
    case_id: str = ""
    layer: str = ""
    attribution: str = Field(..., min_length=1, max_length=64)
    note: str = ""


def _ops_store():
    store = get_ops_store()
    if store:
        store.init_db()
    return store


@router.get("/ops/summary")
def ops_summary() -> dict:
    store = _ops_store()
    trace_count = len(list_trace_ids(5000)) or len(_trace_index)
    badcase_count = 0
    db_backend = settings.ops_db or settings.storage or "memory"
    if store and hasattr(store, "trace_count"):
        trace_count = store.trace_count()
    if store and hasattr(store, "badcase_count"):
        badcase_count = store.badcase_count()
    elif store:
        badcase_count = len(store.badcase_list(500))
    return {
        "db_backend": db_backend,
        "trace_count": trace_count,
        "badcase_count": badcase_count,
    }


@router.get("/ops/skills")
def skill_health() -> dict:
    reg = SkillRegistry()
    stats: dict[str, dict] = {
        sid: {"skill_id": sid, "version": reg.load(sid)["version"], "invocations": 0, "success": 0}
        for sid in reg.list_skills()
    }
    ids = list_trace_ids(500) or _trace_index[-500:]
    for tid in ids:
        tr = get_trace(tid)
        if not tr:
            continue
        for sid in tr.get("skills_invoked", []):
            if sid in stats:
                stats[sid]["invocations"] += 1
                stats[sid]["success"] += 1
    skills = []
    for s in stats.values():
        inv = s["invocations"]
        s["success_rate"] = f"{(s['success']/inv*100):.0f}%" if inv else "—"
        s["fallback_rate"] = "—"
        skills.append(s)
    skills.sort(key=lambda x: -x["invocations"])
    return {"skills": skills, "trace_count": len(ids)}


@router.get("/ops/badcases")
def badcases_list(limit: int = 200) -> dict:
    store = _ops_store()
    if store:
        return {"items": store.badcase_list(min(limit, 500))}
    items = []
    for tid in _trace_index[-100:]:
        tr = get_trace(tid)
        if tr and tr.get("attribution"):
            items.append({"trace_id": tid, "attribution": tr["attribution"]})
    return {"items": items[:50]}


@router.post("/ops/badcases")
def badcases_create(body: BadCaseCreate) -> dict:
    store = _ops_store()
    if not store:
        return {"ok": False, "error": "未配置 OPS_DB 或 AGENTOPS_STORAGE=sqlite|mysql"}
    bid = store.badcase_add(
        trace_id=body.trace_id,
        case_id=body.case_id,
        layer=body.layer,
        attribution=body.attribution,
        note=body.note,
    )
    if body.trace_id:
        tr = get_trace(body.trace_id)
        if tr:
            tr["attribution"] = body.attribution
    return {"id": bid, "ok": True}


@router.post("/ops/badcases/reclassify")
def badcases_reclassify() -> dict:
    """将 eval_failure 等待归类记录按评测层/失败项自动归入七层."""
    store = _ops_store()
    if not store or not hasattr(store, "badcase_reclassify_all"):
        return {"ok": False, "error": "未配置 OPS_DB 或存储不支持批量归类"}
    result = store.badcase_reclassify_all()
    return {"ok": True, **result}
