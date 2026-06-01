# Prompt 版本注册表

> **DEV-010 骨架** | 2026-06-01

## 版本管理规则

- 每个 Skill 独立 Prompt 文件：`skills/prompts/{skill_id}.md`
- 变更必须：更新本表 + 跑 Skill Regression + Eval Harness CI
- 格式：`{skill_id}@semver`（与 Manifest version 对齐）

## 注册表

| Skill ID | Prompt 路径 | 当前版本 | 最后变更 | 变更摘要 | 回归通过率 |
|----------|-------------|----------|----------|----------|-----------|
| intent-classify | `skills/prompts/intent-classify.md` | 1.0.0 | 2026-06-01 | 初版：5 类意图 | — |
| agent-route | `skills/prompts/agent-route.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| knowledge-retrieve | `skills/prompts/knowledge-retrieve.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| answer-compose | `skills/prompts/answer-compose.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| ticket-create | `skills/prompts/ticket-create.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| ticket-query | `skills/prompts/ticket-query.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| ticket-update | `skills/prompts/ticket-update.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| escalation-judge | `skills/prompts/escalation-judge.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| human-handoff | `skills/prompts/human-handoff.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| sentiment-analyze | `skills/prompts/sentiment-analyze.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| crm-lookup | `skills/prompts/crm-lookup.md` | 1.0.0 | 2026-06-01 | 初版 | — |
| compliance-check | `skills/prompts/compliance-check.md` | 1.0.0 | 2026-06-01 | 初版 | — |

## 变更日志

### intent-classify@1.0.0 (2026-06-01)

- 初始版本：consult / ticket / complaint / refund / chitchat

## Replay Diff 记录

| 自版本 | 至版本 | Diff 摘要 | 预期/意外 |
|--------|--------|-----------|-----------|
| — | — | — | — |
