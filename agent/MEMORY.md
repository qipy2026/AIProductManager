# MEMORY — 记忆注入策略

> **Harness Agent Identity v1.0.0** | Memory Router 战术说明  
> 实现：`harness/runtime/memory_injector.py` · `memory/router/`

## 四层 Memory

| 层 | 存储 | 用途 | TTL |
|----|------|------|-----|
| Working | 会话 SQLite/MySQL | 当前对话上下文 | 会话结束 |
| Episodic | 用户维度 | 历史工单号、跨会话指代 | 90 天 |
| Semantic | 向量库 Chroma | FAQ/SOP RAG | 随 KB 版本 |
| Profile | CRM 画像 | VIP 等级、套餐 SLA | 实时同步 |

## 路由与 Skill 依赖

各路由的 `memory_deps` 定义于 `skills/orchestrator/graph.yaml`：

- **consult**：working + semantic
- **consult_vip**：+ profile（消息含 VIP 或 C-1001）
- **ticket_query / complaint**：+ episodic（优先最近工单号）
- **ticket_create / refund**：+ profile + episodic

## 注入规则

1. Orchestrator 在 Skill 链执行 **前** 调用 Memory Injector。
2. `_memory_deps` 由路由键决定，Skill 不得自行扩大 Memory 范围。
3. Episodic 超过 90 天条目 **不注入**，用户需重新描述。
4. Profile 与 Semantic 冲突时 **Profile 优先**（如 VIP SLA 覆盖通用 FAQ）。

## 失败模式

| 症状 | 归因层 | 修复 |
|------|--------|------|
| 用户重复报工单号 | Memory | 检查 episodic 写入（ticket_create 后） |
| 「那个订单」无法关联 | Memory | Working 摘要策略 |
| VIP 未走 consult_vip | Skill/流程 | 路由规则 + L4 用例 |

→ 详见 `docs/11-memory-design.md`
