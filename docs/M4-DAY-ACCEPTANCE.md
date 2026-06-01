# M4 验收清单（6/7）— 运营交付 + Demo

## 交付项

| ID | 项 | 状态 |
|----|-----|------|
| M4-01 | 运营后台 Skill 健康度 API | ✅ GET `/api/ops/skills` |
| M4-02 | Bad Case 列表 API | ✅ GET `/api/ops/badcases` |
| M4-03 | 前端 `/ops` 联调真实数据 | ✅ |
| M4-04 | Trace 查询（对话页 trace_id） | ✅ |
| M4-05 | 跨会话 Episodic（Orchestrator write） | ✅ |
| M4-06 | 客户交付文档包 15~21 | ✅（M0 已完成） |
| M4-07 | E2E 用户路径测试 | ✅ `tests/test_e2e_user_flow.py` |

## Demo 路径（浏览器 :3000）

1. `/chat` — 咨询 / 建单 / 查单 / 投诉 / Guardrail
2. `/ops` — Skill 健康度 + Trace 查询
3. `/eval` — 一键跑评测 + 分层报告 + Replay Diff

## 启动

```bash
# 后端
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8002

# 前端
cd frontend && set BACKEND_URL=http://localhost:8002 && npm run dev
```

## 通过标准

- 三页均可通过 Next 代理访问后端 API
- Eval 门禁 PASS
- pytest 全绿
