# Harness 设计

> **DEV-004** | M0 评审 | 2026-06-01

## Runtime Harness 管道

```
Input Guardrail → Memory Injector → Skill Orchestrator → Skill Executor
  → Tool Validator → Output Guardrail → Trace Recorder
```

## Agent Identity 层（v1.0.0）

人格与战术与代码解耦，统一由 `agent/` 文档包驱动运行时：

| 文档 | 路径 | 用途 |
|------|------|------|
| SOUL | `agent/SOUL.md` | 品牌人格、语气、禁止事项 |
| AGENT | `agent/AGENT.md` | 作战地图：意图路由、Fallback、Eval 对齐 |
| MEMORY | `agent/MEMORY.md` | 四层 Memory 注入策略 |
| TOOLS | `agent/TOOLS.md` | Tool 边界与 Validator |
| 模板 | `agent/templates.yaml` | System Prompt + 固定回复（**运行时加载**） |

加载器：`agent/identity/loader.py` → `identity.system_prompt()` / `identity.template()`

Trace 中记录 `identity_version` 便于 Prompt 层归因与 Replay。

## 模块状态（6/1）

| 模块 | 文件 | 状态 |
|------|------|------|
| Input Guardrail | `harness/runtime/guardrail/input.py` | ✅ 已实现 |
| Output Guardrail | `harness/runtime/guardrail/output.py` | ✅ 已实现 |
| Tool Validator | `harness/runtime/tool_validator.py` | ✅ 已实现 |
| Trace | `harness/runtime/trace.py` | ✅ 已实现 |
| Step Limiter | `harness/runtime/executor.py` | ✅ 已实现 |
| Pipeline | `harness/runtime/pipeline.py` | ✅ 已实现 |
| Memory Injector | `harness/runtime/memory_injector.py` | ✅ 已实现 |
| Eval Harness | `harness/eval/` | ✅ 已实现（120 条 + CI 门禁） |
| Agent Identity | `agent/` + `agent/identity/loader.py` | ✅ 已接入 Runtime |
| MySQL 持久化 | `backend/db/mysql_store.py` + `OPS_DB=mysql` | ✅ Trace/BadCase/对话 |

## Eval Harness 五维断言

Skill / Intent / Tool / Response / Memory

## 七层归因

模型 / Prompt / **Skill** / 知识 / 检索 / 流程 / **Memory**
