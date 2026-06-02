# Agent Identity — Harness 工程文档包

智服通 Agent 的 **人格 + 战术 + 记忆 + 工具** 四层身份定义，供研发、运营与 LLM 运行时统一引用。

## 术语：B2B / 2B / 企业

| 用词 | 正确用法 | 避免 |
|------|----------|------|
| **企业** | 产品能力、客服人设、对用户的话术（「企业智能客服」） | — |
| **B2B** | 客户背景（「某 B2B SaaS 公司」）、作品集定位 | 客服自称「B2B 助手」、回复里写 B2B |
| **2B** | 工程设计语（2B 确定性、2B PRD、2B 约束） | 与 B2B 混写同一句人设描述 |

运行时 `templates.yaml` **不得**出现 B2B；`agent/` 作战/人格文档同理。

## 文档索引

| 文件 | 用途 | 运行时加载 |
|------|------|-----------|
| [SOUL.md](./SOUL.md) | 品牌人格、语气、禁止事项 | `templates.yaml` → `system.*` |
| [AGENT.md](./AGENT.md) | 作战地图：意图路由、Fallback、Eval 对齐 | 人工 + Orchestrator 注释 |
| [MEMORY.md](./MEMORY.md) | 四层 Memory 注入策略 | Memory Injector |
| [TOOLS.md](./TOOLS.md) | Tool 边界与 Validator | Tool Validator |
| [templates.yaml](./templates.yaml) | System Prompt + 固定回复模板 | **`agent.identity.loader`** |

## 代码入口

```python
from agent.identity import identity

identity.system_prompt("compose")   # LLM 回答
identity.template("clarify")        # 澄清话术
identity.doc("SOUL")                # 完整 Markdown（调试/注入）
```

## 变更检查清单

- [ ] 更新 `templates.yaml` version
- [ ] 同步 `docs/10-prompt-registry.md`
- [ ] `pytest tests/test_agent_identity.py`
- [ ] `python -m harness.eval.runner --all`（门禁 ≥85%）

## 与 LangGraph 的关系

`agent/graph.py` 为 LangGraph 编排入口，战术仍以 `AGENT.md` + `graph.yaml` 为准。
