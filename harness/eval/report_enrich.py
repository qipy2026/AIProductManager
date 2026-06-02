"""评测报告 enrichment — 用例元数据 + 归因 + 修复建议."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from backend.badcase.attribution_infer import infer_attribution_from_badcase

CASES_ROOT = Path(__file__).resolve().parents[2] / "evaluation" / "test_cases"
LAYER_DIRS = {
    "L1": "L1_skill",
    "L2": "L2_rag",
    "L3": "L3_tool",
    "L4": "L4_memory",
    "L5": "L5_e2e",
}

LAYER_META = {
    "L1": {"label": "L1 Skill", "desc": "意图路由与 Skill 边界", "focus": "intent-classify / graph.yaml"},
    "L2": {"label": "L2 RAG", "desc": "检索命中与来源引用", "focus": "knowledge-retrieve / 知识库"},
    "L3": {"label": "L3 Tool", "desc": "Tool 参数与 Fallback", "focus": "ticket-* handlers / Validator"},
    "L4": {"label": "L4 Memory", "desc": "Memory 注入与跨会话", "focus": "Memory Router / episodic"},
    "L5": {"label": "L5 E2E", "desc": "端到端业务闭环", "focus": "全链路 + Agent Identity"},
}

_case_cache: dict[str, dict] | None = None


def _load_all_cases() -> dict[str, dict]:
    global _case_cache
    if _case_cache is not None:
        return _case_cache
    cases: dict[str, dict] = {}
    for layer, dirname in LAYER_DIRS.items():
        d = CASES_ROOT / dirname
        if not d.exists():
            continue
        for path in d.glob("*.yaml"):
            with path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            cid = data.get("id", path.stem)
            data.setdefault("layer", layer)
            cases[cid] = data
    _case_cache = cases
    return cases


def infer_fix_hint(failures: list[str], *, layer: str = "", attribution: str = "") -> str:
    text = " ".join(failures).lower()
    if "must_invoke" in text or "must_not_invoke" in text:
        return "检查 intent 路由 → skills/orchestrator/graph.yaml 与对应 Skill handler"
    if "intent expected" in text:
        return "检查 intent-classify 规则/LLM 或 agent/AGENT.md 路由表"
    if "must_inject" in text or "must_not_inject" in text:
        return "检查 Memory Router 与 graph.yaml 中 memory_deps"
    if "source refs" in text or "source" in text:
        return "检查 knowledge-retrieve 阈值与 answer-compose 来源标注"
    if "response must contain" in text or "response must not contain" in text:
        return "检查 Skill 回复模板、知识库片段或 agent/templates.yaml"
    if "blocked" in text:
        return "检查 Input/Output Guardrail 与 agent/templates.yaml"
    if attribution == "retrieval" or layer == "L2":
        return "跑 L2 用例 / 补 FAQ / 调 Semantic 检索"
    if layer == "L3":
        return "检查 Tool Schema、Fallback 模板与 ticket_mock"
    if layer == "L5":
        return "对照 Trace 全链路，优先查 Skill 链与 Eval 断言"
    return "在运营后台查看 Bad Case → Trace → 七层归因"


def get_case_detail(case_id: str) -> dict[str, Any] | None:
    """单条评测用例完整 YAML 内容."""
    cases = _load_all_cases()
    case = cases.get(case_id)
    if not case:
        return None
    layer = case.get("layer", "")
    return {
        "case_id": case_id,
        "layer": layer,
        "description": case.get("description", ""),
        "input": case.get("input") or {},
        "assertions": case.get("assertions") or {},
        "yaml_path": f"evaluation/test_cases/{LAYER_DIRS.get(layer, '')}/{case_id}.yaml",
    }


def enrich_report(raw: dict[str, Any], *, gate: float = 0.85) -> dict[str, Any]:
    cases = _load_all_cases()
    results = raw.get("results") or []
    enriched_results: list[dict[str, Any]] = []

    failure_by_attribution: dict[str, int] = {}
    failure_by_assertion: dict[str, int] = {}

    for r in results:
        cid = r.get("case_id", "")
        case = cases.get(cid, {})
        inp = case.get("input") or {}
        failures = r.get("failures") or []
        layer = r.get("layer") or case.get("layer", "")

        payload = {"layer": layer, "failures": failures, "note": "; ".join(failures)}
        attribution = infer_attribution_from_badcase(payload)

        item = {
            **r,
            "description": case.get("description", ""),
            "message": inp.get("message", ""),
            "input": inp,
            "assertions": case.get("assertions") or {},
            "attribution": attribution,
            "fix_hint": infer_fix_hint(failures, layer=layer, attribution=attribution),
            "yaml_path": f"evaluation/test_cases/{LAYER_DIRS.get(layer, '')}/{cid}.yaml",
        }
        enriched_results.append(item)

        if not r.get("passed", True):
            failure_by_attribution[attribution] = failure_by_attribution.get(attribution, 0) + 1
            for f in failures:
                key = f.split(":")[0].split(" ")[0] if f else "other"
                failure_by_assertion[key] = failure_by_assertion.get(key, 0) + 1

    by_layer = raw.get("by_layer") or {}
    layer_summary = []
    for lid in ("L1", "L2", "L3", "L4", "L5"):
        stats = by_layer.get(lid, {"passed": 0, "failed": 0, "total": 0})
        total = stats.get("total", 0)
        passed = stats.get("passed", 0)
        meta = LAYER_META.get(lid, {"label": lid, "desc": "", "focus": ""})
        layer_summary.append(
            {
                "layer": lid,
                **meta,
                "passed": passed,
                "failed": stats.get("failed", 0),
                "total": total,
                "pass_rate": round(passed / total, 4) if total else 0.0,
            }
        )

    pass_rate = raw.get("pass_rate", 0.0)
    failed = raw.get("failed", 0)

    return {
        **raw,
        "gate": gate,
        "gate_passed": raw.get("gate_passed", pass_rate >= gate),
        "results": enriched_results,
        "layer_summary": layer_summary,
        "failure_by_attribution": failure_by_attribution,
        "failure_by_assertion": failure_by_assertion,
        "failed_cases": [x for x in enriched_results if not x.get("passed")],
        "case_catalog_size": len(cases),
    }
