# 智服通 AgentOps

企业智能客服与工单 Agent 运营中台 — **B2B AI 产品经理作品集**。

## 投递三件套

| # | 内容 | 入口 |
|---|------|------|
| 1 | **能展示** | 本地 [快速启动](#快速启动) · [5 分钟演示路径](#5-分钟演示路径) |
| 2 | **能讲 ROI** | [/roi 业务 ROI](http://localhost:3000/roi) · [VP 汇报样例](./docs/09-roi-report-sample.md) |
| 3 | **有录屏** | **[▶ assets/demo.mp4](./assets/demo.mp4)** · [重生录屏](#产品演示录屏) |

本地启动后访问：**http://localhost:3000**（对话 / 工单 / 业务 ROI / 运营后台 / 评测报告）

## 产品演示录屏

**[assets/demo.mp4](./assets/demo.mp4)** — 约 1.5 分钟 · 1280×720 · 可直接在 GitHub 预览或下载

录屏动线：对话（咨询→建单→查单→投诉→Guardrail）→ 工单中心 → **业务 ROI 总览** → Bad Case 七层 → 评测报告

```powershell
# 自动重生录屏（需前后端 :3000 / :8002 已启动）
.\scripts\record_demo.ps1 -Auto
# 输出 → assets/demo.mp4
```

手动分步 + OBS：`.\scripts\record_demo.ps1` · 分镜见 [scripts/record_demo.md](./scripts/record_demo.md)

## 5 分钟演示路径

```
/chat   咨询 → 建单 → 查单 → 投诉转人工 → Guardrail
/tickets  工单中心（与对话分离）
/roi      业务 ROI 总览（亮点 / 需关注 + 指标详情）
/ops      Bad Case 七层归因 · Trace · Skill 健康度
/eval     120 条评测门禁
```

## 核心能力

- **Skill 编排**：12 Skill + `graph.yaml` 边界矩阵
- **双 Harness**：Runtime（Guardrail / Trace）+ Eval（120 条五维断言 · CI ≥85%）
- **四层 Memory**：Working / Episodic / Semantic / Profile
- **七层 Bad Case 归因**：运营后台可演示、可修复闭环
- **业务 ROI 看板**：基线 vs 当前 vs MVP 目标，总览亮点与待跟进项

## 快速启动

```bash
pip install -r requirements.txt

# 方式 A：Docker 全栈
docker compose up --build
# → http://localhost:3000

# 方式 B：本地开发（Windows）
.\scripts\start_backend_mysql.ps1          # 后端 :8002
cd frontend; $env:BACKEND_URL="http://localhost:8002"; npm run dev
```

```bash
python scripts/run_eval.py --gate 0.85      # 评测门禁
python scripts/seed_badcase_demo.py         # 七层 Bad Case 演示数据
pytest tests/ -q
```

## 对标索引

| 要求 | 交付物 |
|---------|--------|
| Agent / Skill / Workflow 拆解 | [agent/AGENT.md](./agent/AGENT.md) · [docs/13-skill-design.md](./docs/13-skill-design.md) |
| 场景化评测 + 自动化 | [evaluation/](./evaluation/) · [.github/workflows/eval.yml](./.github/workflows/eval.yml) |
| RAG / Tool / 失效判断 | [docs/05-failure-mode-playbook.md](./docs/05-failure-mode-playbook.md) · `/ops` Bad Case |
| 2B PRD / 权限 / 状态机 | [docs/02-PRD-智服通AgentOps.md](./docs/02-PRD-智服通AgentOps.md) · [docs/DELIVERY-INDEX.md](./docs/DELIVERY-INDEX.md) |
| 需求挖掘 + 共创 | [docs/08-requirement-discovery-case.md](./docs/08-requirement-discovery-case.md) · [docs/07-co-creation-workshop-kit.md](./docs/07-co-creation-workshop-kit.md) |
| Bad Case → 归因 → 业务指标 | `/roi` · `/ops` · [docs/09-roi-report-sample.md](./docs/09-roi-report-sample.md) |
| Vibe Coding 可点击 Demo | 本仓库 · [docs/DEMO.md](./docs/DEMO.md) · [assets/demo.mp4](./assets/demo.mp4) |

## 文档

| 文档 | 说明 |
|------|------|
| [PROJECT_PLAN.md](./PROJECT_PLAN.md) | 项目总计划 |
| [docs/DEMO.md](./docs/DEMO.md) | 在线 Demo / 录屏 / 部署 |
| [docs/09-roi-report-sample.md](./docs/09-roi-report-sample.md) | ROI 汇报样例 |
| [docs/](./docs/) | 完整 PRD 与交付包 |

## 目录结构

```
agent/        Agent Identity（SOUL / AGENT / MEMORY / TOOLS）
skills/       Skill Registry + Orchestrator
harness/      Runtime + Eval Harness
backend/      FastAPI · ROI / Bad Case / Tickets API
frontend/     Next.js（chat / tickets / roi / ops / eval）
evaluation/   120 条评测集
assets/       demo.mp4 产品演示录屏
scripts/      启动 · 录屏 · 种子数据
```

## Agent Identity

| 文档 | 说明 |
|------|------|
| [agent/SOUL.md](./agent/SOUL.md) | 品牌人格 |
| [agent/AGENT.md](./agent/AGENT.md) | 作战地图 / 路由表 |
