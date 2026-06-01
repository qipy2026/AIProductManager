# 部署与运维手册

> **文档编号** DOC-AOPS-OPS-001 · **版本** v1.0 · **受众** 客户 IT、运维

---

## 1. 部署架构

### 1.1 推荐拓扑（客户 VPC 私有化）

```
                    ┌─────────────────┐
                    │   WAF / LB      │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Frontend │  │ Backend  │  │ Backend  │
        │ Next.js  │  │ FastAPI  │  │ FastAPI  │
        │  ×2      │  │  ×2      │  │  (HA)    │
        └──────────┘  └────┬─────┘  └──────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ PostgreSQL│     │ Redis    │     │ Qdrant   │
   │ Trace/    │     │ Working  │     │ 向量 KB  │
   │ Memory    │     │ Memory   │     │          │
   └──────────┘     └──────────┘     └──────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              客户工单 API    LLM API（内网/专线）
              客户 CRM API
```

### 1.2 最低配置（MVP / 试运行）

| 组件 | 规格 | 数量 |
|------|------|------|
| Backend | 4C8G | 2 |
| Frontend | 2C4G | 2 |
| PostgreSQL | 4C16G 100GB | 1（主从可选） |
| Redis | 2C4G | 1 |
| 向量库 | 4C8G | 1 |

---

## 2. 部署步骤

### 2.1 前置条件

- [ ] Linux x86_64（Ubuntu 22.04 / CentOS 8+）
- [ ] Docker 24+ 或 K8s 1.28+
- [ ] 出站：LLM API、客户内网 API
- [ ] 域名 + TLS 证书
- [ ] 服务账号 `agentops-svc` 及 API 权限

### 2.2 环境变量

```bash
# .env.production 示例
APP_ENV=production
DATABASE_URL=postgresql://agentops:***@pg.internal:5432/agentops
REDIS_URL=redis://redis.internal:6379/0
VECTOR_DB_URL=http://qdrant.internal:6333
LLM_API_BASE=https://llm.internal/v1
LLM_API_KEY=***
TICKET_API_BASE=https://ticket.internal/api
TICKET_API_KEY=***
CRM_API_BASE=https://crm.internal/api
JWT_SECRET=***
JWT_ISSUER=customer-idp
CORS_ORIGINS=https://agentops.customer.com
TRACE_RETENTION_DAYS=180
EPISODIC_TTL_DAYS=90
```

### 2.3 Docker Compose 部署（示例）

```bash
# 1. 拉取镜像
docker pull registry.vendor.com/agentops-backend:1.0.0
docker pull registry.vendor.com/agentops-frontend:1.0.0

# 2. 初始化数据库
docker compose run --rm backend python scripts/init_db.py

# 3. 导入知识库
docker compose run --rm backend python scripts/import_kb.py /data/kb/

# 4. 启动
docker compose -f docker-compose.prod.yml up -d

# 5. 健康检查
curl -sf https://agentops.customer.com/api/v1/health
```

### 2.4 K8s 部署要点

| 资源 | 副本 | 探针 |
|------|------|------|
| backend | 2+ | `/health` liveness/readiness |
| frontend | 2+ | `/` readiness |
| 配置 | ConfigMap + Secret | 勿明文 Secret |

---

## 3. SLA 与服务等级

### 3.1 可用性（试运行后正式 SLA）

| 等级 | 指标 | 目标 |
|------|------|------|
| 可用性 | 月度 uptime | ≥99.5% |
| 对话 API | P95 延迟 | ≤3s |
| 计划内维护 | 提前通知 | ≥72h |

### 3.2 支持响应

| 级别 | 场景 | 响应 | 解决 |
|------|------|------|------|
| S1 | 生产不可用 | 15min | 4h |
| S2 | 核心功能降级 | 1h | 1 工作日 |
| S3 | 一般问题 | 4h | 3 工作日 |
| S4 | 咨询/优化 | 1 工作日 | 排期 |

### 3.3 维护窗口

- **计划维护**：每周日 02:00–06:00（客户时区）
- **紧急补丁**：与王工确认后执行，事后 24h 内提交变更报告

---

## 4. 监控与告警

### 4.1 监控指标

| 指标 | 告警阈值 |
|------|----------|
| API 错误率 | >1% 持续 5min |
| P95 延迟 | >5s 持续 5min |
| LLM API 失败率 | >5% |
| 工单 API 失败率 | >3% |
| Eval 通过率下降 | <80%（日批） |
| 磁盘使用 | >85% |

### 4.2 日志

| 日志 | 路径/采集 | 保留 |
|------|-----------|------|
| 应用日志 | stdout → ELK | 90 天 |
| Access 日志 | LB | 180 天 |
| Trace | PostgreSQL | 180 天 |
| 审计日志 | 独立索引 | 1 年 |

---

## 5. 备份与恢复

| 数据 | 频率 | RPO | RTO |
|------|------|-----|-----|
| PostgreSQL | 每日全量 + 每小时增量 | 1h | 4h |
| 向量库 | 每周 | 7d | 8h |
| 配置/Secret | 变更时 Git 版本化 | — | 1h |

**恢复演练**：每季度 1 次，王工见证。

---

## 6. 变更与发布

```
开发 → CI（Eval≥85%）→ staging → UAT → 变更委员会（王工）→ 生产
```

| 变更类型 | 审批 | 回滚要求 |
|----------|------|----------|
| Prompt/Skill | PM + 测试 | Replay Diff 存档 |
| 基础设施 | 王工 | 蓝绿/回滚镜像 |
| 紧急热修 | 口头+事后书面 | 30min 内可回滚 |

---

## 7. 运维 Runbook（常见故障）

| 现象 | 排查 | 处理 |
|------|------|------|
| 对话 502 | 查 backend 日志、LLM 连通 | 重启 pod / 切换 LLM |
| 工单创建失败 | Trace 看 Tool 层、调客户 API | 联系客户 IT |
| RAG 全无命中 | 向量库状态、KB 版本 | 重建索引 |
| Eval 骤降 | 最近 Prompt 变更 | Replay Diff 回滚 |
| 内存暴涨 | Redis/会话泄漏 | 清理 + 补丁 |

---

## 8. 培训与移交

| 对象 | 内容 | 时长 |
|------|------|------|
| 坐席 | 对话界面、升级承接 | 30min |
| 主管 | 运营后台、Bad Case | 1h |
| IT | 部署、监控、API | 2h |

**移交清单**：源代码、文档包、密钥清单、监控大盘、On-call 联系人。
