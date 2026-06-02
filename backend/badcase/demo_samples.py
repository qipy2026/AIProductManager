"""七层归因演示 Bad Case — 基于项目真实评测用例与失效模式手册."""

from __future__ import annotations

from typing import Any

DEMO_MARKER = "[七层演示]"

# 每层 1 条，对应用例 / 场景来自 evaluation/test_cases 与 docs/05-failure-mode-playbook.md
DEMO_BADCASES: list[dict[str, Any]] = [
    {
        "case_id": "TC-L1-002",
        "layer": "L1",
        "attribution": "skill",
        "note": f"{DEMO_MARKER} UC-02 报修：用户「设备无法启动」误走 ticket-query，应 invoke ticket-create",
        "failures": [
            "must_not_invoke violated: ticket-query",
            "must_invoke missing: ticket-create",
        ],
    },
    {
        "case_id": "TC-L1-003",
        "layer": "L1",
        "attribution": "prompt",
        "note": f"{DEMO_MARKER} FM-P01 意图模板：「企业版套餐」被识别为 ticket，intent-classify 规则/Prompt 需对齐",
        "failures": ["intent expected consult got ticket"],
    },
    {
        "case_id": "TC-L5-001",
        "layer": "L5",
        "attribution": "model",
        "note": f"{DEMO_MARKER} FM-模型：回复幻觉承诺「24小时无条件退款」，知识库与模板均未授权",
        "failures": ["response must not contain: 无条件退款"],
    },
    {
        "case_id": "TC-L2-004",
        "layer": "L2",
        "attribution": "knowledge",
        "note": f"{DEMO_MARKER} FM-R02 错文档：RAG 命中 FAQ-012 但片段仍为旧版定价，需更新知识库",
        "failures": ["response must contain: 2026 企业版定价"],
    },
    {
        "case_id": "TC-L2-001",
        "layer": "L2",
        "attribution": "retrieval",
        "note": f"{DEMO_MARKER} FM-R04 无来源：knowledge-retrieve 有答案但未输出 source_refs / [1] 引用",
        "failures": ["source refs missing"],
    },
    {
        "case_id": "TC-L3-010",
        "layer": "L3",
        "attribution": "flow",
        "note": f"{DEMO_MARKER} FM-T04 升级流程：投诉场景 human-handoff 队列未命中 VIP 规则，Trace 流程层 403",
        "failures": ["expected blocked=false", "human-handoff queue not assigned"],
    },
    {
        "case_id": "TC-L4-005",
        "layer": "L4",
        "attribution": "memory",
        "note": f"{DEMO_MARKER} FM-M01 跨会话：用户问「上次工单进度」Episodic 未注入 T-001，重复追问",
        "failures": ["must_inject missing: episodic"],
    },
]


def seed_demo_badcases(store: Any) -> dict[str, Any]:
    """写入七层演示 Bad Case（先清除同标记旧数据）."""
    from backend.badcase.attribution_infer import infer_attribution_from_badcase

    deleted = 0
    if hasattr(store, "badcase_delete_by_note_prefix"):
        deleted = store.badcase_delete_by_note_prefix(DEMO_MARKER)

    added = 0
    by_attribution: dict[str, int] = {}
    for sample in DEMO_BADCASES:
        attr = infer_attribution_from_badcase(sample, force=True)
        by_attribution[attr] = by_attribution.get(attr, 0) + 1
        store.badcase_add(
            case_id=sample["case_id"],
            layer=sample["layer"],
            attribution=attr,
            note=sample["note"],
            failures=sample["failures"],
        )
        added += 1

    return {
        "ok": True,
        "deleted": deleted,
        "added": added,
        "by_attribution": by_attribution,
        "marker": DEMO_MARKER,
    }
