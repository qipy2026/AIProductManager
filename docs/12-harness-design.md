# Harness 设计

> **DEV-004** | M0 评审 | 2026-06-01

## Runtime Harness 管道

```
Input Guardrail → Memory Injector → Skill Orchestrator → Skill Executor
  → Tool Validator → Output Guardrail → Trace Recorder
```

## 模块状态（6/1）

| 模块 | 文件 | 状态 |
|------|------|------|
| Input Guardrail | `harness/runtime/guardrail/input.py` | ✅ 已实现 |
| Output Guardrail | `harness/runtime/guardrail/output.py` | ✅ 已实现 |
| Tool Validator | `harness/runtime/tool_validator.py` | ✅ 已实现 |
| Trace | `harness/runtime/trace.py` | ✅ 已实现 |
| Step Limiter | `harness/runtime/executor.py` | ✅ 已实现 |
| Pipeline | `harness/runtime/pipeline.py` | ✅ 已实现 |
| Memory Injector | `harness/runtime/memory_injector.py` | 🔲 6/3 |
| Eval Harness | `harness/eval/` | 🔲 6/4 |

## Eval Harness 五维断言

Skill / Intent / Tool / Response / Memory

## 七层归因

模型 / Prompt / **Skill** / 知识 / 检索 / 流程 / **Memory**
