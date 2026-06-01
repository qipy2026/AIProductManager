# M4 终验收（全功能版）

> 状态：✅ 代码交付完成 · 本地 Demo + CI + Playwright 就绪

## 全量功能清单

| 模块 | 能力 | 路径/命令 |
|------|------|-----------|
| Runtime Harness | Guardrail / Memory / Skill / Trace | `harness/runtime/` |
| Eval Harness | 120 条五维断言 + CI 门禁 | `python scripts/run_eval.py` |
| Memory | Working / Episodic / Profile / Semantic | `memory/stores/` |
| Semantic 向量 | Chroma 持久化（`SEMANTIC_BACKEND=chroma`） | `memory/stores/semantic_chroma.py` |
| SQLite 持久化 | Trace / Ticket / Episodic / BadCase | `backend/db/sqlite_store.py` |
| LLM 适配器 | mock / OpenAI 兼容 | `LLM_MODE=openai` + `backend/llm/` |
| LangGraph Agent | StateGraph 编排 | `USE_LANGGRAPH=1` + `agent/graph.py` |
| Skill ×12 + Prompt | 规则/Mock 可替换 LLM | `skills/` |
| 前端三页 | chat / ops / eval + Tailwind UI | `frontend/` |
| Bad Case | POST/GET 七层归因 | `/api/ops/badcases` |
| Playwright E2E | E2E-001~007 | `cd e2e && npm test` |
| 部署 | Docker / Railway / Vercel | `Dockerfile`, `docker-compose.yml` |
| 录屏指南 | 5 分钟分镜 | `scripts/record_demo.md` |

## 验收命令

```bash
# 评测门禁
python scripts/run_eval.py --gate 0.85

# 单元 + 集成
python -m pytest tests/ -q -k "not e2e_user_flow"

# 生产模式（SQLite + Chroma + LangGraph）
set AGENTOPS_STORAGE=sqlite
set SEMANTIC_BACKEND=chroma
set USE_LANGGRAPH=1
python -m uvicorn backend.main:app --port 8002

# Playwright（需前后端）
cd e2e && npm install && npx playwright install chromium && npm test
```

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `AGENTOPS_STORAGE` | memory | sqlite 启用持久化 |
| `SEMANTIC_BACKEND` | keyword | chroma 启用向量检索 |
| `LLM_MODE` | mock | openai 启用真实 LLM |
| `USE_LANGGRAPH` | 0 | 1 启用 LangGraph 路由 |
| `OPENAI_API_KEY` | — | LLM 必需 |

## 在线部署

1. **Railway**：推送仓库，读取 `railway.toml` + `Dockerfile`
2. **Vercel**：部署 `frontend/`，将 `vercel.json` 中 `YOUR_RAILWAY_BACKEND_URL` 替换为 Railway URL
3. **Docker Compose**：`docker compose up` 一键本地全栈

## 说明

- 评测/CI 默认 **memory + keyword** 保证确定性 120/120
- 生产/Demo 可切换 **sqlite + chroma + langgraph**
- 录屏 mp4 需人工 OBS 或 Playwright headed 模式录制
