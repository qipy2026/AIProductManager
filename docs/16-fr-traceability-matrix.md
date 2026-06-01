# 需求-测试追溯矩阵（RTM）

> **文档编号** DOC-AOPS-RTM-001 · **版本** v1.0  
> **用途**：UAT 验收依据 — 每条功能需求必须映射到测试用例与验收标准  
> **维护**：功能变更时同步更新本矩阵

---

## 1. 追溯说明

| 列 | 含义 |
|----|------|
| FR-ID | PRD 功能需求编号 |
| US-ID | 用户故事编号 |
| TC-ID | 评测/测试用例编号 |
| 类型 | UT / ST / ET / E2E / UAT |
| 验收标准 | 可量化 pass/fail |

**覆盖率目标**：P0 功能需求 **100%** 至少 1 条 ET；P0 **100%** 有 UAT 场景。

---

## 2. 对话与路由

| FR-ID | 需求 | US-ID | TC-ID | 类型 | 验收标准 |
|-------|------|-------|-------|------|----------|
| F-001 | 多轮对话 | US-01 | TC-L4-002, E2E-001 | ET/E2E | 指代消解；≤4 轮 |
| F-002 | 意图识别 | US-01 | TC-L1-003,007,008 | ET | 准确率 ≥90% |
| F-003 | Agent 路由 | US-01 | TC-L1-019, TC-L1-003 | ET | 正确 Agent |
| F-004 | 低置信澄清 | US-01 | TC-L1-024 | ET | 不误建单 |

## 3. 知识问答

| FR-ID | 需求 | US-ID | TC-ID | 类型 | 验收标准 |
|-------|------|-------|-------|------|----------|
| F-010 | RAG 检索 | US-01 | TC-L2-001~025 | ET | 命中率 ≥80% |
| F-011 | 回答生成 | US-01 | TC-L2-025, E2E-001 | ET/E2E | 含 source_refs |
| F-012 | 无命中处理 | US-01 | TC-L2-004 | ET | 不 hallucinate |

## 4. 工单

| FR-ID | 需求 | US-ID | TC-ID | 类型 | 验收标准 |
|-------|------|-------|-------|------|----------|
| F-020 | 工单创建 | US-02 | TC-L1-002, TC-L3-001, E2E-002 | ET/E2E | 字段完整率 ≥95% |
| F-021 | 字段追问 | US-02 | TC-L3-002, E2E-006 | ET/E2E | Fallback 追问 |
| F-022 | 工单查询 | US-03 | TC-L1-001,025, E2E-003 | ET/E2E | 禁止 create |
| F-023 | 工单更新 | US-02 | TC-L1-006,015, TC-L3-005 | ET | 经规则引擎 |

## 5. 升级与投诉

| FR-ID | 需求 | US-ID | TC-ID | 类型 | 验收标准 |
|-------|------|-------|-------|------|----------|
| F-030 | 情绪分析 | US-04 | TC-L1-004,020 | ET | 不决定升级 |
| F-031 | 升级判断 | US-04 | TC-L1-012 | ET | judge 独立 |
| F-032 | 转人工 | US-04 | TC-L1-023, E2E-004 | ET/E2E | 规则执行 |

## 6. Harness

| FR-ID | 需求 | TC-ID | 类型 | 验收标准 |
|-------|------|-------|------|----------|
| F-040 | Input Guardrail | UT-H-001~003, E2E-007 | UT/E2E | 拦截敏感/注入 |
| F-041 | Output Guardrail | UT-H-004 | UT | 无来源警告 |
| F-042 | Tool Validator | UT-H-005~007, TC-L3-007 | UT/ET | Schema+重试 |
| F-043 | Step Limiter | test_executor | UT | 超步数降级 |
| F-044 | Trace | UT-H-009, E2E-008 | UT/E2E | trace_id 可查 |

## 7. Memory

| FR-ID | 需求 | US-ID | TC-ID | 类型 | 验收标准 |
|-------|------|-------|-------|------|----------|
| F-050 | Working Memory | US-01 | TC-L4-002,004 | ET | 指代/摘要 |
| F-051 | Episodic Memory | US-03 | TC-L4-001,005, E2E-005 | ET/E2E | 跨会话 ≥85% |
| F-052 | Profile Memory | US-01 | TC-L4-003, TC-L1-011 | ET | VIP 话术 |
| F-053 | Memory Router | US-03 | TC-L4-007,018,019 | ET | 按需注入 |

## 8. 运营与 Eval

| FR-ID | 需求 | TC-ID | 类型 | 验收标准 |
|-------|------|-------|------|----------|
| F-060 | Skill 健康度 | UAT-OPS-01 | UAT | 面板可展示 |
| F-061 | Trace 可视化 | UAT-OPS-02, E2E-008 | UAT/E2E | 链路完整 |
| F-062 | Bad Case | UAT-OPS-03 | UAT | 七层归因 |
| F-063 | Eval 报告 | TC-L5-023 | ET | 报告可导出 |
| F-070 | 五维断言 | 120 条全集 | ET | 引擎可跑 |
| F-071 | 120 评测集 | TC-L1~L5 | ET | 6/5 齐套 |
| F-072 | CI 门禁 | TC-L5-023 | ET | <85% 阻断 |

## 9. Skill 级追溯（12 Skill）

| Skill ID | FR 关联 | Regression 目录 | 最少用例 |
|----------|---------|-----------------|----------|
| intent-classify | F-002, F-004 | evaluation/skills/intent-classify/ | 25 |
| agent-route | F-003 | evaluation/skills/agent-route/ | 15 |
| knowledge-retrieve | F-010 | evaluation/skills/knowledge-retrieve/ | 25 |
| answer-compose | F-011 | evaluation/skills/answer-compose/ | 20 |
| ticket-create | F-020, F-021 | evaluation/skills/ticket-create/ | 20 |
| ticket-query | F-022 | evaluation/skills/ticket-query/ | 15 |
| ticket-update | F-023 | evaluation/skills/ticket-update/ | 10 |
| escalation-judge | F-031 | evaluation/skills/escalation-judge/ | 15 |
| human-handoff | F-032 | evaluation/skills/human-handoff/ | 10 |
| sentiment-analyze | F-030 | evaluation/skills/sentiment-analyze/ | 10 |
| crm-lookup | F-052 | evaluation/skills/crm-lookup/ | 10 |
| compliance-check | F-040 | evaluation/skills/compliance-check/ | 10 |

## 10. UAT 场景映射

| UAT-ID | 场景 | 覆盖 FR | 执行人 | 预期结果 |
|--------|------|---------|--------|----------|
| UAT-01 | 知识咨询带引用 | F-010,F-011 | 李经理 | 回答含出处 |
| UAT-02 | 报修建单 | F-020,F-021 | 李经理 | 获得工单号 |
| UAT-03 | 查进度不建单 | F-022 | 李经理 | 仅 query |
| UAT-04 | 跨会话续接 | F-051 | 李经理 | 引用历史工单 |
| UAT-05 | 投诉转人工 | F-030~032 | 李经理 | 进入人工队列 |
| UAT-06 | 敏感信息拦截 | F-040 | 王工 | Guardrail 拦截 |
| UAT-07 | API 联调工单 | F-020,F-022 | 王工 | 真实 API 200 |
| UAT-OPS-01 | Skill 健康度 | F-060 | 李经理 | 面板有数据 |
| UAT-OPS-02 | Trace 查询 | F-061 | 王工 | API 返回 steps |
| UAT-OPS-03 | Bad Case 复盘 | F-062 | PM | 归因+修复记录 |

## 11. 覆盖率统计

| 优先级 | FR 总数 | 已追溯 | 覆盖率 |
|--------|---------|--------|--------|
| P0 | 28 | 28 | **100%** |
| P1 | 4 | 4 | **100%** |
| **合计** | **32** | **32** | **100%** |

---

**签字**：测试负责人 ______ 日期 ______ · 客户验收代表 ______ 日期 ______
