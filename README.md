# 智服通 AgentOps

企业智能客服与工单 Agent 运营中台 — B2B AI 产品经理作品集。

## 核心能力

- **Skill 编排体系**：12 个 Skill，边界清晰、可独立评测
- **Agent Harness**：Runtime + Eval 双引擎，可复现、可回归
- **分层 Memory**：Working / Episodic / Semantic / Profile 四层
- **Eval Harness**：120 条评测集 + 五维断言 + CI 门禁

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端（Windows 请用 python -m）
python -m uvicorn backend.main:app --reload --port 8000

# 启动前端（另开终端）
cd frontend && npm install && npm run dev
# 浏览器打开 http://localhost:3000/chat
# 若后端端口非 8000：BACKEND_URL=http://localhost:8001 npm run dev

# 单元测试 + 用户路径 E2E
pytest -v
pytest tests/test_e2e_user_flow.py -v   # 模拟浏览器操作（需前后端均已启动）

# 运行 Eval Harness（后续）
python -m harness.eval.runner --all
```

## 文档

| 文档 | 说明 |
|------|------|
| [JD.md](./JD.md) | 岗位描述 |
| [PROJECT_PLAN.md](./PROJECT_PLAN.md) | 项目总计划 |
| [DEV_TEST_PLAN.md](./DEV_TEST_PLAN.md) | 开发与测试计划（本周冲刺） |
| [docs/](./docs/) | 架构与 PRD 文档 |

## 目录结构

```
skills/     Skill Registry + Orchestrator
harness/    Runtime Harness + Eval Harness
memory/     四层 Memory 体系
agent/      LangGraph Multi-Agent
backend/    FastAPI API
frontend/   Next.js UI
evaluation/ 120 条评测集
```
