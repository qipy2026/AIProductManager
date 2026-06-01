# M1 验收报告（6/2）

> **里程碑**：M1 — `intent-classify` 经 Harness 独立调用 + Trace  
> **自检日期**：2026-06-02  
> **自检结论**：✅ **M1 核心达标** · ⚠️ **S2 全日程部分项顺延 M2**（见 §5）

---

## 1. 为什么说「看起来很快」？

M1 **计划出口准则**（DEV_TEST_PLAN §3.2）只有一条：

> **`intent-classify` Skill 可通过 Harness 独立调用并产出 Trace**

这是 **单 Skill 垂直切片**，不是 M2 的全链路 Agent。所以核心代码量不大，但需用 **测试 + ST 回归** 证明「不是空壳 echo」。

---

## 2. 自动化自检

```bash
python scripts/m1_self_check.py   # 交付物 12/12 + pytest
pytest tests/ -q                  # 63 passed
```

| 检查项 | 结果 |
|--------|------|
| 交付物清单 | **12/12 PASS** |
| pytest 全量 | **63/63 PASS** |
| ST intent-classify | **25/25 PASS（100%，门禁 ≥85%）** |
| UT-H | 9/9 |
| UT-S-001~004 | 8/8 |
| Chat + Trace API | 3/3 |
| E2E 用户路径 | 9/9 |

---

## 3. M1 已交付（对照计划）

| DEV / 项 | 计划 | 实际 |
|----------|------|------|
| DEV-114 Executor 真实 invoke | 6/2 | ✅ `skills/runtime/executor.py` + handler |
| intent-classify 端到端 | 6/2 20:00 | ✅ 规则引擎，Harness → Trace |
| DEV-316 ST 目录 | 6/2 上午 | ✅ `evaluation/skills/intent-classify/` ×25 |
| ST 自动化 | 6/2 17:00 | ✅ `tests/test_intent_classify_st.py` |
| GET `/api/traces/{id}` | UAT-IT-02 | ✅ |
| DEV-233 Trace 面板 | 6/2 | ✅ `TracePanel.tsx`（基础版） |
| UT-S-003~004 | 6/2 | ✅ |
| 替换 echo placeholder | M1 | ✅ |

---

## 4. 手工验收（Demo）

```bash
python -m uvicorn backend.main:app --reload --port 8002
cd frontend && set BACKEND_URL=http://localhost:8002 && npm run dev
```

| 输入 | 预期 |
|------|------|
| 企业版和专业版有什么区别？ | 产品咨询 + 置信度 + trace |
| 帮我查 T-001 进度 | 工单服务 |
| 帮我看看 | 澄清 Fallback |
| 13800138000 | Guardrail 拦截 |
| `/ops` 粘贴 trace_id | guardrail → skill:intent-classify |

---

## 5. 诚实差距（不阻塞 M1，但需知晓）

| 项 | 计划日 | 状态 | 说明 |
|----|--------|------|------|
| **规则引擎 vs LLM** | — | ⚠️ | M1 用规则保证可测；M2 可换 Prompt+LLM |
| **Orchestrator 全链路** | 6/3 | ⏳ M2 | UT-S-005~007 未做 |
| **Memory 注入** | 6/3 | ⏳ M2 | working/episodic 未接 |
| **其余 11 Skill ST** | 6/4+ | ⏳ | 仅 intent-classify 齐 25 条 |
| **L2 评测 YAML 25 条** | 6/2 | ⏳ | 大纲在 14，YAML 未填 |
| **对话 UI 来源引用位** | 6/2 | ⏳ M2 | ChatPanel 无 source_refs |
| **11 份 Prompt 文件** | 6/2 | ⏳ | 仅 intent-classify.md |
| **Skill 健康度真实数据** | 6/4 | ⏳ | `/ops` 仍为占位「—」 |

**结论**：M1 **里程碑签字可过**；若按 **S2 全天 4 泳道** 衡量，完成度约 **~70%**，缺口已标注顺延。

---

## 6. 测试分层一览

```
63 tests
├── UT-H Harness        9
├── UT-S Registry       3
├── UT-S Executor       8  (含 6 条规则 parametrize)
├── ST intent-classify 27 (25 case + count + 85% gate)
├── Chat API            3
├── E2E 用户路径        9
└── Harness Executor    3
```

---

## 7. 签字

| 角色 | M1 核心 | ST 25 条 | 备注 |
|------|---------|----------|------|
| 自动化 | ✅ | ✅ 100% | `m1_self_check.py` |
| 产品负责人 | ⏳ | ⏳ | 手工 Demo §4 |

---

## 8. 6/3 入口（M2）

1. Memory Working Store + Router 注入  
2. `skills/orchestrator/orchestrator.py`  
3. UT-S-005~007 + knowledge-retrieve / ticket-query 首条真实 Skill  
