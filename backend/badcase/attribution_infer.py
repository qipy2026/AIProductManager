"""Bad Case 七层归因推断 — 优先失败断言与评测层，不盲信历史 skill 标签."""

from __future__ import annotations

from typing import Any

KNOWN_LAYERS = frozenset({"model", "prompt", "skill", "knowledge", "retrieval", "flow", "memory"})

ALIAS = {
    "guardrail": "flow",
    "流程": "flow",
}

# 评测分层 → 默认归因（无明确失败项时）
EVAL_LAYER_DEFAULT: dict[str, str] = {
    "L1": "skill",
    "L2": "retrieval",
    "L3": "flow",
    "L4": "memory",
    "L5": "flow",
}


def _norm_failures(item: dict[str, Any]) -> list[str]:
    failures = item.get("failures") or []
    if isinstance(failures, str):
        return [failures] if failures else []
    return [str(f) for f in failures]


def _infer_from_case_yaml(case_id: str, failures: list[str]) -> str | None:
    """结合 YAML 断言类型辅助归因."""
    try:
        from harness.eval.report_enrich import get_case_detail

        detail = get_case_detail(case_id)
    except Exception:
        return None
    if not detail:
        return None
    assertions = detail.get("assertions") or {}
    ftext = " ".join(failures).lower()

    if assertions.get("blocked") is not None and "blocked" in ftext:
        return "flow"
    if assertions.get("memory") and ("inject" in ftext):
        return "memory"
    if assertions.get("source") and "source" in ftext:
        return "retrieval"
    if assertions.get("intent") and "intent" in ftext:
        return "prompt"
    if assertions.get("skill") and ("must_invoke" in ftext or "must_not_invoke" in ftext):
        return "skill"
    if assertions.get("response") and "response must" in ftext:
        layer = (detail.get("layer") or "").upper()
        if layer == "L2":
            return "knowledge" if "source" not in ftext else "retrieval"
        if layer == "L4":
            return "memory"
        if layer == "L3":
            return "flow"
        return "prompt"
    return None


def _infer_from_failures(failures: list[str], layer: str, *, note: str = "") -> str | None:
    """按失败断言文本推断（优先级从高到低）."""
    if not failures:
        return None
    text = " ".join(failures).lower()
    note_lower = note.lower()

    if "blocked" in text or "guardrail" in text or "handoff" in text or "queue" in text:
        return "flow"
    if "must_inject" in text or "must_not_inject" in text:
        return "memory"
    if "source refs" in text:
        return "retrieval"
    if "intent expected" in text:
        return "prompt"
    if "must_invoke" in text or "must_not_invoke" in text:
        return "skill"
    if "response must contain" in text or "response must not contain" in text:
        if any(k in note_lower for k in ("模型", "幻觉", "胡编", "fm-模型")):
            return "model"
        if layer == "L2":
            return "knowledge"
        if layer == "L4":
            return "memory"
        if layer == "L3":
            return "flow"
        if layer == "L5":
            return "prompt"
        return "prompt"

    return None


def infer_attribution_from_badcase(item: dict[str, Any], *, force: bool = False) -> str:
    """根据评测层、失败断言、用例 YAML 推断七层归因.

    force=True 或存在 failures/case_id 时，忽略库内旧 attribution（避免全被标成 skill）.
    """
    failures = _norm_failures(item)
    layer = (item.get("layer") or "").upper()
    case_id = (item.get("case_id") or "").strip()
    raw = (item.get("attribution") or "").strip()
    attr = raw.lower()

    note = item.get("note") or ""
    note_lower = note.lower()

    should_reinfer = force or bool(failures) or bool(case_id) or attr in ("eval_failure", "other", "")

    if should_reinfer:
        if any(k in note_lower for k in ("模型", "幻觉", "胡编", "fm-模型")) and failures:
            return "model"
        if case_id:
            from_yaml = _infer_from_case_yaml(case_id, failures)
            if from_yaml:
                return from_yaml
        from_failures = _infer_from_failures(failures, layer, note=note)
        if from_failures:
            return from_failures
        if layer in EVAL_LAYER_DEFAULT:
            return EVAL_LAYER_DEFAULT[layer]

    if attr and attr not in ("eval_failure", "other", ""):
        if attr in KNOWN_LAYERS:
            return attr
        if attr in ALIAS:
            return ALIAS[attr]
        if raw in ALIAS:
            return ALIAS[raw]

    note = (item.get("note") or "").lower()
    if "guardrail" in note or "blocked" in note or "流程" in note:
        return "flow"
    if "memory" in note or "inject" in note or "episodic" in note:
        return "memory"
    if "检索" in note or "rag" in note or "source" in note or "来源" in note:
        return "retrieval"
    if "知识库" in note or "faq" in note or "错文档" in note:
        return "knowledge"
    if "prompt" in note or "模板" in note or "意图" in note:
        return "prompt"
    if "模型" in note or "幻觉" in note:
        return "model"

    return EVAL_LAYER_DEFAULT.get(layer, "skill")
