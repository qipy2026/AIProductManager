# Agent 架构设计

> **DEV-002** | M0 评审 | 2026-06-01

## 三层能力模型

```
Agent（角色层）→ Skill（能力层）→ Tool（工具层）
```

## Multi-Agent 拓扑

| Agent | 职责 | 挂载 Skill |
|-------|------|-----------|
| 路由 Agent | 意图识别 + 分发 | intent-classify, agent-route |
| 咨询 Agent | 知识问答 | knowledge-retrieve, answer-compose, crm-lookup |
| 工单 Agent | 工单 CRUD | ticket-create, ticket-query, ticket-update |
| 升级 Agent | 投诉升级 | sentiment-analyze, escalation-judge, human-handoff |

## 运行时链路

```
用户 → Runtime Harness → Memory Router → Skill Orchestrator → Agent → Skill → Tool
```

## 知识依赖

| 类型 | 来源 | 用途 |
|------|------|------|
| FAQ/SOP | Semantic Memory | RAG |
| 工单历史 | Episodic Memory | 跨会话 |
| 客户画像 | Profile Memory | VIP/偏好 |

## 评测指标

一次解决率、Skill 路由准确率、RAG 命中率、Memory 命中率、转人工率

→ 详见 `docs/13-skill-design.md` / `docs/11-memory-design.md` / `docs/12-harness-design.md`

## Agent Identity（Harness 工程）

运行时人格与战术见 **`agent/`** 文档包：

- `agent/SOUL.md` — 语气、价值观、禁止事项
- `agent/AGENT.md` — 意图路由、Fallback、Eval 对齐
- `agent/templates.yaml` — LLM System Prompt 与固定模板（由 `agent.identity.loader` 加载）
