"""生成 L1 Skill 路由评测 YAML（25 条）— 对齐 Orchestrator 全链路."""

from pathlib import Path

# (id, desc, message, must_invoke, must_not_invoke, must_contain, must_inject, must_not_inject, user_id, fixture)
CASES = [
    ("TC-L1-001", "查工单", "帮我查一下工单 T-001 的处理进度", ["intent-classify", "ticket-query"], ["ticket-create"], ["T-001"], ["working"], [], "", None),
    ("TC-L1-002", "报修建单", "我要报修，设备无法启动", ["intent-classify", "ticket-create"], ["ticket-query"], ["T-"], ["working"], [], "", None),
    ("TC-L1-003", "知识咨询", "企业版套餐包含哪些功能", ["knowledge-retrieve", "answer-compose"], ["ticket-create"], ["企业版"], ["working", "semantic"], [], "", None),
    ("TC-L1-004", "投诉转人工", "太差了，要投诉", ["sentiment-analyze", "human-handoff"], [], ["转接"], ["working"], [], "", None),
    ("TC-L1-005", "退款建单", "我要退款", ["intent-classify", "ticket-create"], ["ticket-query"], ["T-"], ["working"], [], "", None),
    ("TC-L1-006", "更新工单", "更新 T-002 优先级为高", ["ticket-update"], ["ticket-create"], ["T-002"], ["working"], [], "", None),
    ("TC-L1-007", "闲聊", "今天天气怎么样", ["intent-classify"], ["ticket-create"], ["帮助"], ["working"], [], "", None),
    ("TC-L1-008", "澄清", "帮我看看", ["intent-classify"], ["ticket-create"], ["咨询"], ["working"], [], "", None),
    ("TC-L1-009", "宕机报修", "服务器宕机了", ["ticket-create"], ["answer-compose"], ["T-"], ["working"], [], "", None),
    ("TC-L1-010", "查单", "查一下 T-005 进度", ["ticket-query"], [], ["T-005"], ["working"], [], "", None),
    ("TC-L1-011", "VIP SLA", "我是 VIP，SLA 是多少", ["crm-lookup", "knowledge-retrieve", "answer-compose"], ["ticket-create"], ["SLA"], ["working", "semantic", "profile"], [], "user_vip", {"user_id": "user_vip", "profile": {"tier": "VIP", "plan": "企业版"}}),
    ("TC-L1-012", "升级判断", "三次没解决，找经理", ["escalation-judge"], ["human-handoff"], ["反馈"], ["working"], [], "", None),
    ("TC-L1-013", "合规", "如何绕过审核流程", ["compliance-check"], ["ticket-create"], ["合规"], ["working"], [], "", None),
    ("TC-L1-014", "CRM", "查客户 C-1001 信息", ["crm-lookup"], ["ticket-create"], ["C-1001"], ["working"], [], "", None),
    ("TC-L1-015", "关闭工单", "关闭 T-003 工单", ["ticket-update"], ["ticket-create"], ["T-003"], ["working"], [], "", None),
    ("TC-L1-016", "发票", "如何开具发票", ["knowledge-retrieve", "answer-compose"], ["ticket-create"], ["发票"], ["working", "semantic"], [], "", None),
    ("TC-L1-017", "密码 FAQ", "忘记密码怎么办", ["knowledge-retrieve", "answer-compose"], ["ticket-create"], ["密码"], ["working", "semantic"], [], "", None),
    ("TC-L1-018", "退款查单", "我要退款，顺便查 T-010", ["ticket-query"], [], ["T-010"], ["working"], [], "", None),
    ("TC-L1-019", "问候路由", "你好", ["intent-classify"], ["ticket-create"], ["帮助"], ["working"], [], "", None),
    ("TC-L1-020", "情绪建单", "很生气，订单没发货", ["sentiment-analyze", "ticket-create"], [], ["T-"], ["working"], [], "", None),
    ("TC-L1-021", "版本对比", "企业版和专业版区别", ["knowledge-retrieve", "answer-compose"], ["ticket-create"], ["企业版"], ["working", "semantic"], [], "", None),
    ("TC-L1-022", "套餐咨询", "专业版有什么功能", ["knowledge-retrieve", "answer-compose"], [], ["专业版"], ["working", "semantic"], [], "", None),
    ("TC-L1-023", "升级转人工", "三次没解决要投诉", ["human-handoff"], [], ["转接"], ["working"], [], "", None),
    ("TC-L1-024", "低置信", "嗯", ["intent-classify"], ["ticket-create"], ["咨询"], ["working"], [], "", None),
    ("TC-L1-025", "查进度禁建", "工单处理到哪了", ["ticket-query"], ["ticket-create"], ["工单"], ["working"], [], "", None),
]


def yaml_list(items: list[str]) -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"    - {x}" for x in items)


def render(case: tuple) -> str:
    cid, desc, msg, inv, not_inv, contain, inject, not_inject, uid, fx = case
    import json
    uid_line = f'  user_id: "{uid}"\n' if uid else ""
    fx_block = json.dumps(fx, ensure_ascii=False) if fx else "null"
    return f"""id: {cid}
layer: L1
description: {desc}
input:
  message: "{msg}"
{uid_line}  memory_fixture: {fx_block}
assertions:
  skill:
    must_invoke:{yaml_list(inv)}
    must_not_invoke:{yaml_list(not_inv)}
  response:
    must_contain:{yaml_list(contain)}
  memory:
    must_inject:{yaml_list(inject)}
    must_not_inject:{yaml_list(not_inject)}
"""


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "evaluation" / "test_cases" / "L1_skill"
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        path = out / f"{case[0]}.yaml"
        path.write_text(render(case), encoding="utf-8")
    print(f"Generated {len(CASES)} L1 cases in {out}")


if __name__ == "__main__":
    main()
