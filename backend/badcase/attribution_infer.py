"""Bad Case 七层归因推断 — Eval 失败记录自动归类."""

from __future__ import annotations

from typing import Any

KNOWN_LAYERS = frozenset({"model", "prompt", "skill", "knowledge", "retrieval", "flow", "memory"})

ALIAS = {
    "guardrail": "flow",
    "流程": "flow",
}


def infer_attribution_from_badcase(item: dict[str, Any]) -> str:
    """根据评测层、失败断言推断七层归因."""
    raw = (item.get("attribution") or "").strip()
    attr = raw.lower()

    if attr and attr not in ("eval_failure", "other", ""):
        if attr in KNOWN_LAYERS:
            return attr
        if attr in ALIAS:
            return ALIAS[attr]
        if raw in ALIAS:
            return ALIAS[raw]

    layer = (item.get("layer") or "").upper()
    failures = item.get("failures") or []
    if isinstance(failures, str):
        failures = [failures]
    note = item.get("note") or ""
    text = " ".join(str(f) for f in failures) + " " + str(note)
    tl = text.lower()

    if "blocked" in tl or "guardrail" in tl:
        return "flow"
    if "must_inject" in tl or "must_not_inject" in tl or layer == "L4":
        return "memory"
    if "source refs" in tl or layer == "L2":
        return "retrieval"
    if layer == "L1":
        return "skill"
    if layer == "L3":
        return "skill" if ("must_invoke" in tl or "must_not_invoke" in tl) else "flow"
    if layer == "L5":
        if "source" in tl:
            return "retrieval"
        if "inject" in tl or "memory" in tl:
            return "memory"
        if "intent" in tl or "invoke" in tl:
            return "skill"
        return "flow"
    if "intent expected" in tl or "must_invoke" in tl or "must_not_invoke" in tl:
        return "skill"
    if "response must contain" in tl or "response must not contain" in tl:
        return "skill"
    return "skill"
