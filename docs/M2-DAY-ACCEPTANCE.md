# M2 验收报告（6/3–6/4）

> **里程碑**：MVP 端到端 — 咨询 / 建单 / 查单 / 升级  
> **状态**：✅ 开发完成 · 待手工验收

---

## 1. M2 交付（相对 M1 增量）

| 模块 | 交付 |
|------|------|
| **Memory 四层** | working / episodic / profile / semantic |
| **Memory Router** | 按 Skill deps + 意图注入（consult 不注 episodic） |
| **Harness Injector** | Trace 含 memory_injected |
| **Orchestrator** | intent → Skill 链（graph.yaml） |
| **Skill Handlers** | retrieve / compose / ticket-create / ticket-query / escalation / handoff |
| **Mock** | `knowledge-base/faq.json` + `ticket_mock.py` |
| **前端** | 对话页展示 📎 来源引用 |

---

## 2. 自动化测试

```bash
python scripts/m2_self_check.py
pytest tests/ -q    # 79 passed
```

| 套件 | 数量 | 覆盖 |
|------|------|------|
| UT-M | 9 | Memory 001~008 |
| UT-S Orchestrator | 5 | 005~007 + 投诉 + Fallback |
| Chat API | 5 | 四场景 + Trace |
| M1 存量 | 60 | Harness / ST / E2E |

---

## 3. MVP 四场景手工验收

| # | 输入 | 预期 Skill 链 | 预期回复 |
|---|------|---------------|----------|
| 1 | 企业版和专业版有什么区别？ | classify → retrieve → compose | 含套餐差异 + 📎 FAQ-012 |
| 2 | 服务器宕机请尽快处理 | classify → ticket-create | 返回新工单号 T-xxx |
| 3 | 查 T-001 进度 | classify → ticket-query | 状态 in_progress，**不新建单** |
| 4 | 太差了三次没解决 | classify → judge → handoff | 转人工话术 |
| 5 | 我要报修 | ticket-create fallback | 追问 title/优先级 |
| 6 | 13800138000 | Guardrail | 敏感拦截 |

---

## 4. 启动 Demo

```powershell
python -m uvicorn backend.main:app --reload --port 8002
cd frontend
$env:BACKEND_URL="http://localhost:8002"
npm run dev
```

---

## 5. 未做（M3+）

- Eval Harness Runner + CI
- L2~L5 YAML 全量
- Episodic 跨会话 E2E-005 自动化
- 向量库真实 embedding
- LangGraph Agent 独立模块（逻辑已并入 Orchestrator）

---

## 6. 6/5 入口（M3）

Eval Harness 引擎 + 120 条 CI 门禁
