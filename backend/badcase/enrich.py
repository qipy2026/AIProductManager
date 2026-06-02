"""Bad Case 列表 enrichment — 七层归因 + 修复建议."""

from __future__ import annotations

from typing import Any

from backend.badcase.attribution_infer import infer_attribution_from_badcase
from harness.eval.report_enrich import infer_fix_hint

LAYER_META = {
    "model": {"label": "模型层", "focus": "换模型 / 调温度 / Replay"},
    "prompt": {"label": "Prompt 层", "focus": "改 agent/templates.yaml / Prompt 版本"},
    "skill": {"label": "Skill 层", "focus": "改 graph.yaml / Skill handler"},
    "knowledge": {"label": "知识层", "focus": "更新 FAQ / 文档审计"},
    "retrieval": {"label": "检索层", "focus": "调 RAG 阈值 / 补文档"},
    "flow": {"label": "流程层", "focus": "Guardrail / 状态机 / Tool 权限"},
    "memory": {"label": "Memory 层", "focus": "Memory Router / L4 回归"},
}


def enrich_badcase(item: dict[str, Any]) -> dict[str, Any]:
    failures = item.get("failures") or []
    if isinstance(failures, str):
        failures = [failures]
    layer = item.get("layer") or ""
    attribution = infer_attribution_from_badcase({**item, "failures": failures}, force=True)
    meta = LAYER_META.get(attribution, {})
    return {
        **item,
        "failures": failures,
        "attribution": attribution,
        "attribution_label": meta.get("label", attribution),
        "fix_hint": infer_fix_hint(failures, layer=layer, attribution=attribution),
        "attribution_focus": meta.get("focus", ""),
    }


def enrich_badcase_list(items: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = [enrich_badcase(x) for x in items]
    by_attribution: dict[str, int] = {}
    for x in enriched:
        key = x.get("attribution") or "other"
        by_attribution[key] = by_attribution.get(key, 0) + 1
    return {
        "items": enriched,
        "total": len(enriched),
        "by_attribution": by_attribution,
    }
