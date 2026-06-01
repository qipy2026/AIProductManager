"""生成 L2~L5 评测 YAML（95 条）— 对齐当前 Orchestrator 能力."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "evaluation" / "test_cases"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def yaml_list(items: list) -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"    - {x}" for x in items)


def gen_l2() -> None:
    cases = [
        ("TC-L2-001", "企业版套餐", "企业版套餐包含哪些功能", ["企业版"], ["ticket-create"]),
        ("TC-L2-002", "版本对比", "企业版和专业版区别", ["专业版", "企业版"], []),
        ("TC-L2-003", "发票 FAQ", "如何开具发票", ["发票"], []),
        ("TC-L2-004", "密码重置", "忘记密码怎么办", ["密码"], []),
        ("TC-L2-005", "VIP SLA", "VIP 客户 SLA 是多少", ["SLA"], []),
        ("TC-L2-006", "同义词", "专业版有什么功能", ["专业版"], []),
        ("TC-L2-007", "无命中", "火星移民政策如何办理", ["抱歉", "未找到"], []),
        ("TC-L2-008", "来源标记", "套餐说明", ["来源"], []),
        ("TC-L2-009", "引用编号", "企业版和专业版", ["[1]"], []),
        ("TC-L2-010", "多关键词", "企业版 技术支持", ["企业版"], []),
    ]
    for i in range(11, 26):
        cases.append((f"TC-L2-{i:03d}", f"咨询变体{i}", "企业版套餐功能", ["企业版"], []))

    for cid, desc, msg, contain, not_sk in cases:
        src_min = 0 if cid == "TC-L2-007" else 1
        w(ROOT / "L2_rag" / f"{cid}.yaml", f"""id: {cid}
layer: L2
description: {desc}
input:
  message: "{msg}"
  session_id: "l2-{cid}"
assertions:
  skill:
    must_invoke:
      - knowledge-retrieve
      - answer-compose
    must_not_invoke:{yaml_list(not_sk)}
  response:
    must_contain:{yaml_list(contain)}
  source:
    min_count: {src_min}
""")


def gen_l3() -> None:
    specs = [
        ("TC-L3-001", "创建工单", "服务器宕机请处理", ["ticket-create"], ["T-"], []),
        ("TC-L3-002", "缺字段 Fallback", "我要报修", ["ticket-create"], ["补充", "标题"], []),
        ("TC-L3-003", "查询工单", "查 T-001 进度", ["ticket-query"], ["T-001"], ["ticket-create"]),
        ("TC-L3-004", "退款建单", "我要退款", ["ticket-create"], ["T-"], ["ticket-query"]),
        ("TC-L3-005", "更新工单", "更新 T-002 优先级为高", ["ticket-update"], ["T-002"], ["ticket-create"]),
        ("TC-L3-006", "关闭工单", "关闭 T-003 工单", ["ticket-update"], ["T-003"], []),
        ("TC-L3-007", "查进度禁创建", "工单处理到哪了", ["ticket-query"], ["工单"], ["ticket-create"]),
        ("TC-L3-008", "紧急优先级", "设备故障紧急", ["ticket-create"], ["T-"], []),
        ("TC-L3-009", "CRM", "查客户 C-1001 信息", ["crm-lookup"], ["C-1001"], ["ticket-create"]),
        ("TC-L3-010", "升级转人工", "太差了要投诉", ["human-handoff"], ["人工", "转接"], []),
    ]
    for i in range(11, 26):
        specs.append((f"TC-L3-{i:03d}", f"建单变体{i}", "网络异常无法访问", ["ticket-create"], ["T-"], []))

    for cid, desc, msg, inv, contain, not_inv in specs:
        w(ROOT / "L3_tool" / f"{cid}.yaml", f"""id: {cid}
layer: L3
description: {desc}
input:
  message: "{msg}"
assertions:
  skill:
    must_invoke:{yaml_list(inv)}
    must_not_invoke:{yaml_list(not_inv)}
  response:
    must_contain:{yaml_list(contain)}
""")


def gen_l4() -> None:
    specs = [
        ("TC-L4-001", "working 注入", "你好", "", ["working"], [], None),
        ("TC-L4-002", "consult 无 episodic", "企业版区别", "u4", ["working", "semantic"], ["episodic"], None),
        ("TC-L4-003", "query 含 episodic", "查 T-001", "u1", ["working", "episodic"], [], {"user_id": "u1", "episodic": [{"summary": "历史工单 T-099", "ticket_ids": ["T-099"]}]}),
        ("TC-L4-004", "VIP profile", "VIP SLA 多少", "user_vip", ["profile", "semantic"], [], None),
        ("TC-L4-005", "跨会话续接", "上次工单进度呢", "u2", ["working", "episodic"], [], {"user_id": "u2", "episodic": [{"summary": "曾咨询 T-001", "ticket_ids": ["T-001"]}]}),
    ]
    for i in range(6, 21):
        specs.append((f"TC-L4-{i:03d}", f"memory-{i}", "企业版功能", "u4", ["working", "semantic"], ["episodic"], None))

    for cid, desc, msg, uid, must_inj, must_not, fx in specs:
        if fx:
            import json
            fx_block = json.dumps(fx, ensure_ascii=False)
        else:
            fx_block = "null"
        w(ROOT / "L4_memory" / f"{cid}.yaml", f"""id: {cid}
layer: L4
description: {desc}
input:
  message: "{msg}"
  user_id: "{uid}"
  memory_fixture: {fx_block}
assertions:
  memory:
    must_inject:{yaml_list(must_inj)}
    must_not_inject:{yaml_list(must_not)}
""")


def gen_l5() -> None:
    specs = [
        ("TC-L5-001", "E2E 咨询", "企业版和专业版区别", ["knowledge-retrieve"], ["企业版"]),
        ("TC-L5-002", "E2E 建单", "服务器宕机", ["ticket-create"], ["T-"]),
        ("TC-L5-003", "E2E 查单", "查 T-001 进度", ["ticket-query"], ["in_progress"]),
        ("TC-L5-004", "E2E 升级", "三次没解决要投诉", ["human-handoff"], ["转接"]),
        ("TC-L5-005", "E2E Guardrail", "我的密码是abc123", [], ["敏感"]),
        ("TC-L5-006", "E2E 澄清", "帮我看看", ["intent-classify"], ["咨询"]),
        ("TC-L5-007", "E2E 退款", "我要退款", ["ticket-create"], ["T-"]),
        ("TC-L5-008", "E2E 发票", "如何开发票", ["answer-compose"], ["发票"]),
        ("TC-L5-009", "E2E 闲聊", "你好", [], ["帮助"]),
        ("TC-L5-010", "E2E Fallback", "我要报修", ["ticket-create"], ["补充"]),
    ]
    for i in range(11, 26):
        specs.append((f"TC-L5-{i:03d}", f"e2e-{i}", "企业版功能咨询", ["answer-compose"], ["企业版"]))

    for cid, desc, msg, inv, contain in specs:
        blocked = "Guardrail" in desc
        blocked_line = "\n  blocked: true" if blocked else ""
        w(ROOT / "L5_e2e" / f"{cid}.yaml", f"""id: {cid}
layer: L5
description: {desc}
input:
  message: "{msg}"
assertions:{blocked_line}
  skill:
    must_invoke:{yaml_list(inv)}
  response:
    must_contain:{yaml_list(contain)}
""")


def main() -> None:
    gen_l2()
    gen_l3()
    gen_l4()
    gen_l5()
    print("Generated L2~L5 cases")


if __name__ == "__main__":
    main()
