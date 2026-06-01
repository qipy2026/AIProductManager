# 测试用例大纲 — 120 条评测集

> **DEV-014 / D 泳道** | M0 产出 | 日期：2026-06-01  
> 与 `docs/13-skill-design.md` Skill 边界矩阵一一对应

---

## 统计

| 层级 | 代号 | 数量 | 断言类型 | 目录 |
|------|------|------|----------|------|
| L1 | Skill 路由 | 25 | Skill Assertion | `evaluation/test_cases/L1_skill/` |
| L2 | RAG 召回 | 25 | Response + Source | `evaluation/test_cases/L2_rag/` |
| L3 | Tool 调用 | 25 | Tool Assertion | `evaluation/test_cases/L3_tool/` |
| L4 | Memory | 20 | Memory Assertion | `evaluation/test_cases/L4_memory/` |
| L5 | 端到端 | 25 | 五维组合 | `evaluation/test_cases/L5_e2e/` |
| **合计** | | **120** | | |

**填充计划**：6/1 骨架 → 6/2 L1+L3 → 6/3 L4 → 6/4 L2+L5(10) → 6/5 齐套

---

## L1 · Skill 路由（25 条）

| ID | 标题 | 输入摘要 | must_invoke | must_not_invoke |
|----|------|----------|-------------|-----------------|
| TC-L1-001 | 查工单进度 | 查 T-001 进度 | ticket-query | ticket-create |
| TC-L1-002 | 创建工单 | 我要报修，设备无法启动 | ticket-create | ticket-query |
| TC-L1-003 | 知识咨询 | 企业版套餐包含哪些功能 | knowledge-retrieve | ticket-create |
| TC-L1-004 | 投诉升级 | 太差了，要投诉 | sentiment-analyze | human-handoff |
| TC-L1-005 | 退款意图 | 我要退款 | ticket-create | ticket-query |
| TC-L1-006 | 修改工单 | 更新 T-002 优先级 | ticket-update | ticket-create |
| TC-L1-007 | 纯闲聊 | 今天天气怎么样 | intent-classify | ticket-create |
| TC-L1-008 | ambiguous 咨询 | 帮我看看 | intent-classify | ticket-create |
| TC-L1-009 | 报修意图 | 服务器宕机了 | ticket-create | answer-compose |
| TC-L1-010 | 查询+创建混合 | 查进度，不行就新建 | ticket-query | — |
| TC-L1-011 | VIP 咨询 | VIP 客户问 SLA | knowledge-retrieve, crm-lookup | ticket-create |
| TC-L1-012 | 升级判断 | 三次未解决要经理 | escalation-judge | human-handoff |
| TC-L1-013 | 合规拦截 | 如何绕过审核 | compliance-check | ticket-create |
| TC-L1-014 | CRM 查询 | 查客户 C-1001 信息 | crm-lookup | ticket-create |
| TC-L1-015 | 关闭工单 | 关闭 T-003 | ticket-update | ticket-create |
| TC-L1-016 | 发票咨询 | 如何开具发票 | knowledge-retrieve | ticket-create |
| TC-L1-017 | 密码重置 | 忘记密码 | knowledge-retrieve | ticket-create |
| TC-L1-018 | 多意图-优先工单 | 退款且查进度 | ticket-query | — |
| TC-L1-019 | 路由 Agent | 任意输入 | agent-route | ticket-create |
| TC-L1-020 | 情绪+工单 | 很生气，订单没发货 | sentiment-analyze, ticket-create | — |
| TC-L1-021 | 仅检索不回复 | （内部）retrieve 阶段 | knowledge-retrieve | answer-compose |
| TC-L1-022 | 仅生成不检索 | （内部）compose 阶段 | answer-compose | knowledge-retrieve |
| TC-L1-023 | 升级执行 | 判定需升级后 | human-handoff | escalation-judge |
| TC-L1-024 | 低置信澄清 | 嗯 | intent-classify | ticket-create |
| TC-L1-025 | 边界-查询非创建 | 工单处理到哪了 | ticket-query | ticket-create, ticket-update |

---

## L2 · RAG 召回（25 条）

| ID | 标题 | 场景 | 预期 |
|----|------|------|------|
| TC-L2-001 | 精确命中 FAQ | 退款多久到账 | 引用 FAQ-001 |
| TC-L2-002 | 精确命中 SOP | 工单升级流程 | 引用 SOP-010 |
| TC-L2-003 | 部分命中 | 套餐价格（多版本） | 引用+说明版本 |
| TC-L2-004 | 无命中 | 火星移民政策 | 转人工提示 |
| TC-L2-005 | 冲突文档 | 退款 7 天 vs 15 天 | 说明以最新为准 |
| TC-L2-006 | 多文档综合 | 企业版功能对比 | ≥2 来源 |
| TC-L2-007 | 产品手册 | API 限流规则 | 引用手册章节 |
| TC-L2-008 | 同义词检索 | 怎么退钱 | 命中退款 FAQ |
| TC-L2-009 | 英文查询 | refund policy | 命中英文 FAQ |
| TC-L2-010 | 长尾问题 | 数据导出格式 | 部分命中 |
| TC-L2-011 | 过时文档 | 2023 年价格 | 标注可能过时 |
| TC-L2-012 | 权限相关 | 管理员权限说明 | 引用 RBAC 文档 |
| TC-L2-013 | 空知识库 | （fixture 空库） | 无命中处理 |
| TC-L2-014 | Top-K 边界 | 宽泛问题 | ≤K 条来源 |
| TC-L2-015 | 相似度阈值 | 边缘相关问题 | 低于阈值不引用 |
| TC-L2-016 | 表格内容 | 套餐对比表 | 结构化引用 |
| TC-L2-017 | 代码片段 | Webhook 示例 | 引用技术文档 |
| TC-L2-018 | 多轮追问 | 那专业版呢 | 继承上轮上下文 |
| TC-L2-019 | 敏感知识 | 内部定价 | 脱敏回复 |
| TC-L2-020 | 检索超时 | （mock 超时） | 降级模板 |
| TC-L2-021 | 重复文档 | 两篇相同 FAQ | 去重引用 |
| TC-L2-022 | 跨语言文档 | 中文问英文档 | 翻译+引用 |
| TC-L2-023 | 版本化知识 | v2.0 新功能 | 引用 v2.0 |
| TC-L2-024 | 禁止 hallucinate | 无文档支撑 | 不得编造政策 |
| TC-L2-025 | Source 格式 | 任意命中 | source_refs 非空 |

---

## L3 · Tool 调用（25 条）

| ID | 标题 | Tool | 关键断言 |
|----|------|------|----------|
| TC-L3-001 | 创建工单-完整 | ticket_api.create | priority=normal |
| TC-L3-002 | 创建工单-缺字段 | ticket_api.create | Fallback 追问 |
| TC-L3-003 | 创建 VIP 工单 | ticket_api.create | priority=high |
| TC-L3-004 | 查询工单 | ticket_api.get | ticket_id 正确 |
| TC-L3-005 | 更新优先级 | ticket_api.update | 仅 update |
| TC-L3-006 | CRM 查询 | crm_api.get_customer | 只读 |
| TC-L3-007 | 参数类型错误 | ticket_api.create | Validator 重试 |
| TC-L3-008 | API 5xx | ticket_api.create | Retry + Fallback |
| TC-L3-009 | 权限拒绝 | ticket_api.create | 403 处理 |
| TC-L3-010 | 重复建单 | ticket_api.create | 幂等/提示 |
| TC-L3-011 | 无效工单号 | ticket_api.get | 友好错误 |
| TC-L3-012 | 批量字段 | ticket_api.create | 全部必填 |
| TC-L3-013 | 合规校验 | compliance-check | 拦截后不调 Tool |
| TC-L3-014 | 状态机-新建 | ticket_api.create | status=new |
| TC-L3-015 | 状态机-禁止跳转 | ticket_api.update | 规则引擎拦截 |
| TC-L3-016 | 转人工 | human-handoff API | 规则执行 |
| TC-L3-017 | JSON Schema | ticket_api.create | schema 校验 |
| TC-L3-018 | 超时重试 | ticket_api.create | ≤3 次 |
| TC-L3-019 | 并发建单 | ticket_api.create | 无冲突 |
| TC-L3-020 | CRM 不存在 | crm_api.get | 404 处理 |
| TC-L3-021 | 附件字段 | ticket_api.create | attachment_url |
| TC-L3-022 | 分类字段 | ticket_api.create | category 枚举 |
| TC-L3-023 | 时间戳 | ticket_api.create | created_at 自动 |
| TC-L3-024 | 禁止 LLM 改状态 | ticket_api.update | 规则引擎 |
| TC-L3-025 | Tool Trace | 任意 | Trace 含 tool 层 |

---

## L4 · Memory（20 条）

| ID | 标题 | Fixture | 断言 |
|----|------|---------|------|
| TC-L4-001 | 跨会话续接 | 昨日工单 T-001 | 引用 T-001 |
| TC-L4-002 | 指代消解 | Working 含订单号 | 「那个订单」关联 |
| TC-L4-003 | VIP 识别 | Profile=VIP | 高优先级话术 |
| TC-L4-004 | 长对话压缩 | 15 轮 Working | 摘要后信息不丢 |
| TC-L4-005 | Episodic 过期 | 91 天前 | 不注入 |
| TC-L4-006 | Profile 冲突 | 新旧套餐 | Profile 优先 |
| TC-L4-007 | Memory 失效归因 | 无 Episodic | 归因 memory 层 |
| TC-L4-008 | Token 预算 | 多层注入 | ≤ 预算上限 |
| TC-L4-009 | 退款续问 | Episodic 退款会话 | 注入 episodic |
| TC-L4-010 | 纯 FAQ 无 Episodic | 知识问答 | 不注入 episodic |
| TC-L4-011 | PII 脱敏写入 | 会话结束 | 摘要去 PII |
| TC-L4-012 | 用户删记忆 | 请求删除 | Forget Policy |
| TC-L4-013 | Working 归档 | 会话关闭 | → Episodic |
| TC-L4-014 | Semantic 版本 | 知识更新 | 版本号正确 |
| TC-L4-015 | 偏好渠道 | Profile 偏好邮件 | 话术体现 |
| TC-L4-016 | 多用户隔离 | user A/B | 不串记忆 |
| TC-L4-017 | 空 Profile | 新用户 | 默认策略 |
| TC-L4-018 | Router 按需 | 工单进度 | working+episodic |
| TC-L4-019 | Router 最小 | 简单问候 | 仅 working |
| TC-L4-020 | Memory Trace | 任意 | Trace 含注入层 |

---

## L5 · 端到端（25 条）

| ID | 标题 | 旅程 | 五维 |
|----|------|------|------|
| TC-L5-001 | 咨询→满意结束 | FAQ 问答 | 全 |
| TC-L5-002 | 咨询→建单 | 无法 FAQ 解决 | 全 |
| TC-L5-003 | 建单→查进度 | 多轮 | 全 |
| TC-L5-004 | 投诉→升级 | 转人工 | 全 |
| TC-L5-005 | 跨会话续接 E2E | 两 session | Memory |
| TC-L5-006 | Guardrail 拦截 E2E | 敏感输入 | Skill+Guard |
| TC-L5-007 | Fallback 追问 E2E | 缺字段建单 | Tool+Skill |
| TC-L5-008 | RAG 无命中 E2E | 未知问题 | Response |
| TC-L5-009 | VIP 全流程 | VIP 投诉建单 | 全 |
| TC-L5-010 | 多 Skill 编排 | 咨询转工单 | Skill |
| TC-L5-011 | Harness 降级 | LLM 超时 | Trace |
| TC-L5-012 | 15 轮长对话 | 摘要+解决 | Memory |
| TC-L5-013 | 并发会话 | 同用户两 tab | Memory |
| TC-L5-014 | 工单状态流转 | 新建→处理中 | Tool+规则 |
| TC-L5-015 | 合规退款 | 金额规则引擎 | Skill |
| TC-L5-016 | Bad Case 复盘 | 故意失败 | 归因 |
| TC-L5-017 | Replay Diff | 版本对比 | RT |
| TC-L5-018 | 一次解决率 | 标准 FAQ | 指标 |
| TC-L5-019 | 转人工率 | 边界案例 | 指标 |
| TC-L5-020 | 平均轮次 | 简单咨询 | ≤4 轮 |
| TC-L5-021 | 响应时间 | 标准请求 | ≤3s |
| TC-L5-022 | 运营面板 Trace | 完整链路 | 可视化 |
| TC-L5-023 | Eval CI 门禁 | PR 触发 | CI |
| TC-L5-024 | 部署环境 E2E | staging | E2E |
| TC-L5-025 | 录屏场景 | Demo 脚本 | 人工 |

---

## Skill 级 Regression 索引（12 Skill）

| Skill | 用例数 | 目录 | 计划完成 |
|-------|--------|------|----------|
| intent-classify | 25 | `evaluation/skills/intent-classify/` | 6/2 |
| agent-route | 15 | `evaluation/skills/agent-route/` | 6/3 |
| knowledge-retrieve | 25 | `evaluation/skills/knowledge-retrieve/` | 6/3 |
| answer-compose | 20 | `evaluation/skills/answer-compose/` | 6/4 |
| ticket-create | 20 | `evaluation/skills/ticket-create/` | 6/2 |
| ticket-query | 15 | `evaluation/skills/ticket-query/` | 6/3 |
| ticket-update | 10 | `evaluation/skills/ticket-update/` | 6/4 |
| escalation-judge | 15 | `evaluation/skills/escalation-judge/` | 6/4 |
| human-handoff | 10 | `evaluation/skills/human-handoff/` | 6/5 |
| sentiment-analyze | 10 | `evaluation/skills/sentiment-analyze/` | 6/5 |
| crm-lookup | 10 | `evaluation/skills/crm-lookup/` | 6/4 |
| compliance-check | 10 | `evaluation/skills/compliance-check/` | 6/5 |

---

## E2E 录屏场景（8 条 · 对应 TC-L5-022~025 + E2E-001~008）

| E2E ID | 映射 TC | 录屏必拍 |
|--------|---------|----------|
| E2E-001 | TC-L5-001 | ✅ |
| E2E-002 | TC-L5-002 | ✅ |
| E2E-003 | TC-L5-003 | ✅ |
| E2E-004 | TC-L5-004 | ✅ |
| E2E-005 | TC-L5-005 | ✅ |
| E2E-006 | TC-L5-007 | ✅ |
| E2E-007 | TC-L5-006 | ✅ |
| E2E-008 | TC-L5-022 | ✅ |
