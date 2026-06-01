# Skill 体系设计

> **DEV-003** | M0 评审 | 2026-06-01

## 12 Skill 注册表

| Skill ID | Agent | does_not（边界） |
|----------|-------|-----------------|
| intent-classify | 路由 | 不生成回复、不调 Tool |
| agent-route | 路由 | 不执行业务 Skill |
| knowledge-retrieve | 咨询 | 不生成最终回复 |
| answer-compose | 咨询 | 不检索、不建单 |
| ticket-create | 工单 | 不查询/修改/关闭 |
| ticket-query | 工单 | 不创建/修改 |
| ticket-update | 工单 | 不创建 |
| escalation-judge | 升级 | 不直接转人工 |
| human-handoff | 升级 | 不做业务处理 |
| sentiment-analyze | 投诉 | 不决定升级策略 |
| crm-lookup | 共用 | 不修改 CRM |
| compliance-check | Harness | 不做业务回复 |

## 编排 ADR

1. **检索与生成分离** — 检索失败可单独归因
2. **judge 与 handoff 分离** — 判断 LLM，执行规则
3. **intent-classify 独立** — 路由变更不影响业务 Skill

## Manifest 规范

见 `skills/manifests/schema.json`

## Skill 级评测

每个 Skill 独立 Regression 集 → `evaluation/skills/{skill_id}/`
