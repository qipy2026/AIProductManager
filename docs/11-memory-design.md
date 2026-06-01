# Memory 体系设计

> **DEV-005** | M0 评审 | 2026-06-01

## 四层架构

| 层级 | 生命周期 | 典型用途 |
|------|---------|---------|
| Working | 会话级 | 多轮指代、当前上下文 |
| Episodic | 用户 90 天 | 跨会话续接、历史工单 |
| Semantic | 持久 | RAG 知识库 |
| Profile | 持久 | VIP、套餐、偏好 |

## Memory Router

按 `Skill.memory_deps` + 意图按需注入，Token 预算控制。

## Policy

| 策略 | 规则 |
|------|------|
| Write | Working→Episodic 摘要+去 PII |
| Summarize | Working >8 轮自动压缩 |
| Forget | Episodic 90 天 TTL |
| Conflict | Profile > Episodic |

## 实现计划

6/3：`memory/stores/` + `memory/router/` + Harness Injector
