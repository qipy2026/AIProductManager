"""生成 intent-classify Skill 级回归用例（ST × 25）— DEV-316 / S2 17:00."""

from pathlib import Path

CASES = [
    ("ST-IC-001", "套餐咨询", "企业版套餐包含哪些功能", "consult", 0.85, False),
    ("ST-IC-002", "版本对比", "企业版和专业版有什么区别", "consult", 0.85, False),
    ("ST-IC-003", "发票 FAQ", "如何开具发票", "consult", 0.85, False),
    ("ST-IC-004", "密码重置", "忘记密码怎么办", "consult", 0.85, False),
    ("ST-IC-005", "VIP SLA", "我是 VIP，SLA 是多少", "consult", 0.85, False),
    ("ST-IC-006", "报修建单", "我要报修，设备无法启动", "ticket", 0.85, False),
    ("ST-IC-007", "宕机", "服务器宕机了请尽快处理", "ticket", 0.85, False),
    ("ST-IC-008", "查进度 T号", "帮我查一下工单 T-001 的处理进度", "ticket", 0.85, False),
    ("ST-IC-009", "查进度语义", "工单处理到哪了", "ticket", 0.70, False),
    ("ST-IC-010", "投诉", "太差了，要投诉", "complaint", 0.85, False),
    ("ST-IC-011", "激烈投诉", "三次没解决，找经理", "complaint", 0.85, False),
    ("ST-IC-012", "退款", "我要退款", "refund", 0.90, False),
    ("ST-IC-013", "退钱", "请帮我退钱", "refund", 0.90, False),
    ("ST-IC-014", "闲聊天气", "今天天气怎么样", "chitchat", 0.85, False),
    ("ST-IC-015", "打招呼", "你好", "chitchat", 0.85, False),
    ("ST-IC-016", "模糊澄清", "帮我看看", "unknown", 0.35, True),
    ("ST-IC-017", "单字澄清", "嗯", "unknown", 0.35, True),
    ("ST-IC-018", "空泛", "啊", "unknown", 0.35, True),
    ("ST-IC-019", "更新工单", "更新 T-002 优先级为高", "ticket", 0.85, False),
    ("ST-IC-020", "关闭工单", "关闭 T-003 工单", "ticket", 0.85, False),
    ("ST-IC-021", "情绪+工单", "很生气，订单没发货", "complaint", 0.85, False),
    ("ST-IC-022", "CRM 模糊", "客户 C-1001 的资料", "unknown", 0.40, True),
    ("ST-IC-023", "合规敏感", "如何绕过审核流程", "unknown", 0.55, True),
    ("ST-IC-024", "混合退款查单", "我要退款，顺便查 T-010", "refund", 0.90, False),
    ("ST-IC-025", "路由问候", "您好，在吗", "chitchat", 0.85, False),
]


def render(case: tuple) -> str:
    cid, desc, msg, intent, min_conf, clarify = case
    return f"""id: {cid}
skill: intent-classify
description: {desc}
input:
  message: "{msg}"
assertions:
  intent: {intent}
  min_confidence: {min_conf}
  needs_clarify: {'true' if clarify else 'false'}
  boundary:
    must_not_set_response: true
    must_not_invoke_tools: true
"""


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "evaluation" / "skills" / "intent-classify"
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        (out / f"{case[0]}.yaml").write_text(render(case), encoding="utf-8")
    print(f"Generated {len(CASES)} ST cases -> {out}")


if __name__ == "__main__":
    main()
