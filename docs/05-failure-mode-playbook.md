# 失效模式诊断手册

> **DEV-009（部分）** | 2026-06-01

## 七层归因索引

| 层级 | 典型症状 | 诊断入口 |
|------|----------|----------|
| 模型 | 回复风格漂移、胡言乱语 | 换模型 Replay Diff |
| Prompt | 特定场景稳定失败 | Prompt Registry 版本对比 |
| **Skill** | 该调不调 / 跨界调用 | Skill Assertion 报告 |
| 知识 | 内容错误但检索正常 | 知识库版本审计 |
| 检索 | 无命中 / 错文档 | L2 RAG 评测集 |
| 流程 | 状态机/权限错误 | 流程 Trace |
| **Memory** | 重复描述 / 指代失败 | L4 Memory Fixture |

---

## 1. RAG / 检索失效

| 模式 | 现象 | 根因 | 修复 |
|------|------|------|------|
| FM-R01 无命中 | 「找不到相关信息」 | 阈值过高 / 文档缺失 | 降阈值或补文档 |
| FM-R02 错文档 | 引用了过期 FAQ | 版本未同步 | Semantic Memory 版本 pin |
| FM-R03 冲突文档 | 两个相反答案 | 知识库冲突 | 冲突消解规则 + 人工审核 |
| FM-R04 无来源引用 | 回答正确但无 citation | Output Guardrail 未生效 | 强制 source_refs |
| FM-R05 检索超时 | 响应 >3s | 向量库性能 | 缓存 + 降 Top-K |

## 2. Tool Call 失效

| 模式 | 现象 | 根因 | 修复 |
|------|------|------|------|
| FM-T01 参数幻觉 | 编造 ticket_id | LLM 幻觉 | Tool Validator + Schema |
| FM-T02 缺字段 | 建单失败 | 提取不全 | Skill Fallback 追问 |
| FM-T03 API 5xx | 重试后失败 | 下游故障 | Retry + 降级模板 |
| FM-T04 权限拒绝 | 403 | RBAC | 归因流程层 |
| FM-T05 跨界调用 | query 时 create | Skill 边界 | Skill Assertion 回归 |

## 3. 长上下文 / Memory 失效

| 模式 | 现象 | 根因 | 修复 |
|------|------|------|------|
| FM-M01 重复描述 | 用户重复说问题 | Episodic 未注入 | Memory Router 规则 |
| FM-M02 指代失败 | 「那个订单」未关联 | Working 丢失 | 摘要策略优化 |
| FM-M03 上下文爆炸 | Token 超限 | 未压缩 | 8 轮 Summarize |
| FM-M04 过期记忆 | 引用 91 天前 | TTL | Forget Policy |
| FM-M05 Profile 冲突 | 旧套餐覆盖新 | 冲突策略 | Profile 优先 |

## 4. Skill / 流程失效

| 模式 | 现象 | 根因 | 修复 |
|------|------|------|------|
| FM-S01 路由错误 | 咨询走了建单 | intent-classify | L1 回归 |
| FM-S02 超步数循环 | 无限追问 | 无 Step Limiter | executor 降级 |
| FM-S03 Guardrail 漏网 | 敏感信息泄露 | 词库不全 | 更新 Guardrail |

## 5. 诊断流程

```
Bad Case 录入 → Harness Trace 拉取 → 自动归因标签
  → 命中 FM-xx → 执行 Playbook 修复 → Eval 回归 → 关闭
```
