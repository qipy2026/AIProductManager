# AGENT — 作战地图

> **Harness Agent Identity v1.0.0** | 运行时路由与战术边界  
> 可执行配置：`skills/orchestrator/graph.yaml` · 模板：`agent/templates.yaml`

## 1. 使命

在 **Runtime Harness** 管道内，将用户输入稳定路由到正确 Skill 链，输出可溯源、可评测、可运营的企业客服回复。

```
Input Guardrail → Memory Inject → intent-classify → Route → Skill Chain → Output Guardrail → Trace
```

## 2. Multi-Agent 分工

| Agent | 职责 | 挂载 Skill |
|-------|------|-----------|
| router-agent | 意图识别 + 分发 | intent-classify, agent-route |
| consult-agent | 知识问答 | knowledge-retrieve, answer-compose, crm-lookup |
| ticket-agent | 工单 CRUD | ticket-create, ticket-query, ticket-update |
| escalation-agent | 投诉升级 | sentiment-analyze, escalation-judge, human-handoff |

## 3. 意图 → 路由表

| 意图 | 路由键 | Skill 链 | Memory 层 |
|------|--------|----------|-----------|
| consult | consult / consult_vip | knowledge-retrieve → answer-compose | working, semantic (+ profile if VIP) |
| ticket (query) | ticket_query | ticket-query | working, episodic |
| ticket (list) | ticket_query | ticket-query（列表模式） | working, episodic |
| ticket (create) | ticket_create | ticket-create | working, profile |
| ticket (update) | ticket_update | ticket-update | working |
| complaint | complaint / complaint_judge | sentiment → judge → handoff（或仅 judge） | working, episodic |
| refund | refund | ticket-create | working, profile, episodic |
| crm | crm | crm-lookup | working, profile |
| compliance | compliance | compliance-check | working |
| chitchat | chitchat | agent-route（+ LLM 兜底） | working |
| unknown / 低置信 | clarify | 无 Skill，模板澄清 | working |

### 3.1 特殊路由规则（代码层 `_route_key`）

| 条件 | 路由键 | 说明 |
|------|--------|------|
| 消息含「生气」+「订单」，且无「投诉」 | angry_ticket | 先建单再安抚 |
| 消息含 VIP | consult_vip | 注入 Profile + CRM |
| 退款 + 工单号 T-xxx | ticket_query | 优先查单而非建退款单 |
| 含「投诉」或「太差」 | complaint | 全链升级 |
| 仅情绪无明确投诉词 | complaint_judge | 记录反馈，不一定转人工 |

## 4. 战术边界（必须遵守）

### 4.1 可以做

- 基于知识库片段回答咨询（须带 📎 来源）
- 按 Schema 创建/查询/更新工单（Tool Validator 校验）
- 识别情绪并建议升级 / 转人工
- 澄清低置信意图（`needs_clarify`）

### 4.2 禁止做

- **LLM 直接修改工单状态**（状态机由规则引擎执行，见 ADR-001）
- 编造知识库不存在的内容
- 绕过 Guardrail 处理敏感输入
- 在 compliance 场景提供违规指引
- Skill 跨界（如 answer-compose 不检索、不建单）

## 5. Fallback 策略

| 场景 | 模板键 | 触发 |
|------|--------|------|
| 意图不明 | `clarify` | confidence < 0.6 或 unknown |
| 报修信息不足 | `ticket_create_fallback` | 仅「我要报修」 |
| 缺工单号 | `ticket_query_fallback` | 无法提取 T-xxx |
| 查看工单列表 | ticket-query 列表模式 | 「查看我的工单列表」等 |
| RAG 无命中 | `no_kb_hit` | chunks 为空 |
| 投诉待跟进 | `complaint_judge` | complaint_judge 路由无 response |
| 升级转人工 | `human_handoff` | human-handoff Skill |
| 合规拦截 | `compliance_blocked` | compliance-check |
| 闲聊 | `chitchat_greeting` | LLM 关闭时的兜底 |

## 6. 与 Eval Harness 对齐

| Eval 层 | 验证点 |
|---------|--------|
| L1 Skill | 意图路由、Skill 边界 |
| L2 RAG | 检索命中、来源引用 |
| L3 Tool | 参数 Schema、Fallback |
| L4 Memory | Profile/VIP/Episodic 注入 |
| L5 E2E | 全链路 + 人格一致性 |

## 7. 失效诊断

出问题时按 Trace → 七层归因查：

1. Guardrail 拦截？→ 输入层
2. 意图错？→ intent-classify / Prompt
3. Skill 链错？→ graph.yaml + L1
4. 回答无来源？→ Output Guardrail + answer-compose
5. 重复描述？→ Memory 注入（见 MEMORY.md）

→ 详见 `docs/05-failure-mode-playbook.md`
