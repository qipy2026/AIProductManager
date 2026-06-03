# 智服通 AgentOps

> 企业智能客服与工单 Agent 运营中台 — B2B AI 产品经理作品集

把「我想搞点 AI 客服」落地为**可嵌入工单 / 知识库 / 运营后台**的业务闭环：Skill 定边界、Harness 保回归、Memory 保连续、Eval + ROI 证效果。

---

## 产品经理工作流

```
需求洞察 → 方案定义 → 原型验证 → 效果度量 → 交付验收 → 本地体验
```

| 阶段 | 目标 | 关键动作 | 入口 |
|------|------|----------|------|
| **1. 需求洞察** | 厘清真实业务问题与决策约束 | 需求访谈 · 共创工作坊 · 场景优先级排序 | [需求挖掘案例](./docs/08-requirement-discovery-case.md) · [共创工坊](./docs/07-co-creation-workshop-kit.md) |
| **2. 方案定义** | 输出可评审、可落地的 Agent 方案 | PRD · Skill 边界 · 状态机 · 权限与异常路径 | [PRD](./docs/02-PRD-智服通AgentOps.md) · [架构](./docs/01-agent-architecture.md) · [Skill 设计](./docs/13-skill-design.md) |
| **3. 原型验证** | 验证主路径可行、可向客户演示 | 可点击 Demo · 录屏 · Guardrail 场景走查 | [▶ demo.mp4](./assets/demo.mp4) · [演示手册](./docs/DEMO.md) · [5 分钟路径](#5-分钟演示路径) |
| **4. 效果度量** | 用数据证明试点成效 | ROI 看板 · 120 条评测门禁 · Bad Case 七层归因 | [/roi](http://localhost:3000/roi) · [/eval](http://localhost:3000/eval) · [ROI 汇报样例](./docs/09-roi-report-sample.md) |
| **5. 交付验收** | 满足 2B 交付与客户签收标准 | PRD 套件 · API 规格 · UAT 计划 | [交付索引](./docs/DELIVERY-INDEX.md) · [UAT 计划](./docs/17-uat-acceptance-plan.md) |
| **6. 本地体验** | 评审者可独立复现 Demo | Docker / 本地启动 · 跑通主路径 | [快速启动](#快速启动) |

---

## 背景与目标用户

**场景**：B2B 企业客服 — 咨询答疑、工单创建/查询、投诉升级、敏感信息拦截。

**用户角色**

| 角色 | 诉求 | 产品入口 |
|------|------|----------|
| 终端客户 | 快速解决问题、少重复描述 | `/chat` |
| 客服主管 | 工单分流、处理进度可见 | `/tickets` |
| 运营 / PM | Bad Case 归因、Skill 健康度 | `/ops` |
| 业务负责人 | 试点 ROI、基线 vs 目标 | `/roi` |
| 质量 / 研发 | 可回归评测、CI 门禁 | `/eval` |

**MVP 目标**：一次解决率 ↑、转人工率 ↓、评测通过率 ≥85%，Bad Case 可闭环。

---

## 方案概览

```
用户对话 ──→ Runtime Harness（Guardrail → Memory → Skill 编排 → Trace）
                │
                ├── 工单系统（/tickets）
                ├── 运营中台（/ops：Bad Case · Trace · Skill）
                ├── 业务 ROI（/roi：基线 → 当前 → 目标）
                └── Eval Harness（/eval：120 条 · 五维断言 · CI）
```

**核心设计决策**

- **Skill 编排**：12 Skill + 边界矩阵，意图路由可评测、可解释
- **双 Harness**：Runtime 保生产可控；Eval 保迭代可回归
- **四层 Memory**：Working / Episodic / Semantic / Profile
- **七层 Bad Case 归因**：从 Prompt 到 Tool 的分层诊断 → 业务指标联动

---

## 5 分钟演示路径

本地启动后访问 **http://localhost:3000**，按序体验：

| 步骤 | 路径 | 验证点 |
|------|------|--------|
| 1 | `/chat` | 咨询 · 建单 · 查单 · 投诉转人工 · Guardrail |
| 2 | `/tickets` | 工单与对话分离，状态可追溯 |
| 3 | `/roi` | 总览亮点/需关注，点击指标看详情 |
| 4 | `/ops` | Bad Case 七层（可载入演示数据） |
| 5 | `/eval` | 全量评测报告与门禁 |

**产品录屏**：[assets/demo.mp4](./assets/demo.mp4)（约 1.5 分钟 · 1280×720）

```powershell
# 重生录屏（前后端 :3000 / :8002 已启动）
.\scripts\record_demo.ps1 -Auto
```

---

## 效果度量（怎么证明做成了）

| 维度 | 指标 | 在哪里看 |
|------|------|----------|
| **业务** | 一次解决率、转人工率、人均日工单等 | `/roi` · [ROI 样例报告](./docs/09-roi-report-sample.md) |
| **质量** | 120 条用例通过率、门禁 ≥85% | `/eval` · `python scripts/run_eval.py --gate 0.85` |
| **运营** | Bad Case 数量、七层归因分布 | `/ops` · `python scripts/seed_badcase_demo.py` |
| **工程** | Skill 调用量、Trace 全链路 | `/ops` Trace 诊断 |

---

## 快速启动

```bash
pip install -r requirements.txt

# Docker 全栈
docker compose up --build
# → http://localhost:3000

# 本地开发（Windows）
.\scripts\start_backend_mysql.ps1
cd frontend; $env:BACKEND_URL="http://localhost:8002"; npm run dev
```

```bash
python scripts/run_eval.py --gate 0.85
python scripts/seed_badcase_demo.py
pytest tests/ -q
```

---

## 交付物索引

| 类型 | 文档 |
|------|------|
| 规划 | [PROJECT_PLAN.md](./PROJECT_PLAN.md) |
| 需求 | [PRD](./docs/02-PRD-智服通AgentOps.md) · [流程/状态机](./docs/03-workflow-and-state-machine.md) |
| 设计 | [架构](./docs/01-agent-architecture.md) · [Harness](./docs/12-harness-design.md) · [Memory](./docs/11-memory-design.md) · [ADR](./docs/06-design-decision-records.md) |
| 失效与归因 | [Failure Playbook](./docs/05-failure-mode-playbook.md) |
| 接口 | [API 规格](./docs/15-api-specification.md) |
| 演示 | [DEMO.md](./docs/DEMO.md) · [录屏分镜](./scripts/record_demo.md) |
| Agent | [SOUL](./agent/SOUL.md) · [AGENT](./agent/AGENT.md) · [MEMORY](./agent/MEMORY.md) · [TOOLS](./agent/TOOLS.md) |

完整清单 → [docs/DELIVERY-INDEX.md](./docs/DELIVERY-INDEX.md)

---

## 仓库结构

```
docs/         PRD · 架构 · 评测 · ROI · 交付包
agent/        Agent Identity（SOUL / AGENT / MEMORY / TOOLS）
skills/       Skill Registry + Orchestrator
harness/      Runtime + Eval Harness
backend/      FastAPI（Chat · Tickets · ROI · Bad Case）
frontend/     Next.js（chat / tickets / roi / ops / eval）
evaluation/   120 条评测集
assets/       demo.mp4 产品演示录屏
scripts/      启动 · 录屏 · 种子数据
```
