# TOOLS — 工具边界

> **Harness Agent Identity v1.0.0** | Tool API 与 Validator 规则  
> 实现：`backend/tools/` · `harness/runtime/tool_validator.py`

## 可用 Tool

| Tool | Skill 调用方 | 权限 | Schema 要点 |
|------|-------------|------|-------------|
| ticket_api.create | ticket-create | 写 | title, priority 必填 |
| ticket_api.get | ticket-query | 读 | ticket_id |
| ticket_api.update | ticket-update | 写（规则校验） | status 流转受状态机约束 |
| semantic_store.search | knowledge-retrieve | 读 | query → chunks |
| crm（Profile） | crm-lookup | 读 | customer_id / tier |

## Validator 规则

1. 必填字段缺失 → Skill Fallback 追问（不调用 Tool）
2. 类型错误 → 重试最多 3 次 → 降级模板
3. API 5xx → 重试 → 「系统繁忙，请稍后再试」
4. **禁止** LLM 输出未在 Schema 中的字段直接传入 Tool

## Skill ↔ Tool 矩阵

| Skill | 可调 Tool | 不可调 |
|-------|-----------|--------|
| intent-classify | 无 | 全部 |
| knowledge-retrieve | semantic search | ticket |
| answer-compose | 无 | 全部 |
| ticket-* | ticket_api | semantic |
| human-handoff | 无（标记 handoff） | 改工单状态 |

## 2B 约束（企业侧确定性）

- 工单状态 **new → in_progress → closed / escalated** 由规则引擎校验
- 退款/财务类操作 **仅** ticket-create 建单，不 LLM 直批

> 「2B」= 卖给企业客户的产品约束（合规、可审计），**不是**对终端用户的自称用语。

→ 详见 `docs/03-workflow-and-state-machine.md`
