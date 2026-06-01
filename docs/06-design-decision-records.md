# 架构决策记录（ADR）

> **DEV-009** | 2026-06-01

## ADR-001：工单状态流转使用规则引擎

- **状态**：已接受
- **背景**：2B 不允许 LLM 随意变更工单状态
- **决策**：`ticket-update` Skill 仅提取意图，状态变更由 `backend/rules/engine.py` 执行
- **后果**：Skill 边界清晰，需维护规则表

## ADR-002：检索与生成拆分为两个 Skill

- **状态**：已接受
- **背景**：检索失败需单独归因，不应污染生成评测
- **决策**：`knowledge-retrieve` + `answer-compose` 分离
- **后果**：多一次 Skill 调用，评测更精确

## ADR-003：escalation-judge 与 human-handoff 分离

- **状态**：已接受
- **背景**：升级判断可 LLM，执行必须确定性
- **决策**：judge 用 LLM；handoff 用规则引擎
- **后果**：Workflow 多一跳，合规可控

## ADR-004：Eval 环境 Mock LLM

- **状态**：已接受
- **背景**：LLM 非确定性导致 CI 波动
- **决策**：Eval Harness 使用 Mock LLM；Skill/Tool 层断言为主
- **后果**：需维护 Mock；生产与 Eval 共享 Guardrail/Validator

## ADR-005：Memory 写入摘要 + 去 PII

- **状态**：已接受
- **背景**：个保法 / GDPR，不能原文持久化敏感对话
- **决策**：Working→Episodic 必须摘要 + PII 脱敏
- **后果**：跨会话可能丢细节，需 Profile 补全

## ADR-006：Harness Step Limiter 上限 10 步

- **状态**：已接受
- **背景**：Agent 循环导致成本失控
- **决策**：`executor.py` MAX_STEPS=10，超限降级模板
- **后果**：复杂多轮可能提前终止，需人工接手

## LLM 禁区地图（汇总）

| 环节 | LLM | 规则/Skill |
|------|-----|-----------|
| 意图识别 | ✅ + 阈值 | 低置信→澄清 |
| RAG 检索 | ✅ | — |
| 回复生成 | ✅ | 需来源 |
| 工单状态 | ❌ | 规则引擎 |
| 退款金额 | ❌ | compliance-check |
| 转人工执行 | ❌ | human-handoff |
| Memory 写入 | 摘要 | Policy 审核 |
