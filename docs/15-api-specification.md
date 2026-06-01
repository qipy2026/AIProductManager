# API 接口规格说明书

> **文档编号** DOC-AOPS-API-001 · **版本** v1.0 · **受众** 客户 IT、集成开发  
> **Base URL**：`https://agentops.{customer-domain}/api/v1`（生产）  
> **Staging**：`https://agentops-staging.{customer-domain}/api/v1`

---

## 1. 通用约定

### 1.1 协议与安全

| 项 | 规范 |
|----|------|
| 协议 | HTTPS only（TLS 1.2+） |
| 认证 | `Authorization: Bearer {jwt}`（生产必选） |
| 租户 | Header `X-Tenant-Id`（多租户预留） |
| 请求 ID | Header `X-Request-Id`（UUID，便于 Trace 关联） |
| 字符集 | UTF-8 |
| 时间 | ISO 8601 UTC，`2026-06-01T08:00:00Z` |

### 1.2 统一响应 envelope

**成功（HTTP 200/201）**

```json
{
  "code": 0,
  "message": "ok",
  "data": { },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**业务错误（HTTP 4xx）**

```json
{
  "code": 40001,
  "message": "ticket field validation failed",
  "data": {
    "errors": ["missing required field: priority"]
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**系统错误（HTTP 5xx）**

```json
{
  "code": 50001,
  "message": "upstream ticket service unavailable",
  "data": null,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 1.3 错误码

| code | HTTP | 说明 | 客户端处理 |
|------|------|------|-----------|
| 0 | 200 | 成功 | — |
| 40001 | 400 | 参数校验失败 | 修正输入 |
| 40101 | 401 | 未认证 | 刷新 Token |
| 40301 | 403 | 无权限 | 提示联系管理员 |
| 40401 | 404 | 资源不存在 | 提示工单号错误 |
| 42901 | 429 | 限流 | 退避重试 |
| 50001 | 500 | 内部错误 | 重试 + 上报 |
| 50002 | 502 | 上游工单/CRM 不可用 | 降级话术 |

---

## 2. AgentOps 对话 API

### 2.1 POST `/chat` — 发送消息

**描述**：用户发送一条消息，经 Harness → Skill 编排后返回 Agent 回复及 Trace 元数据。

**Request Headers**

```
Authorization: Bearer eyJhbG...
Content-Type: application/json
X-Request-Id: 550e8400-e29b-41d4-a716-446655440000
```

**Request Body**

```json
{
  "message": "帮我查一下工单 T-20260601-001 的处理进度",
  "session_id": "sess_8f3a2b1c",
  "user_id": "user_10086",
  "channel": "web",
  "metadata": {
    "client_version": "1.0.0",
    "locale": "zh-CN"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | ✅ | 1–4000 字符 |
| session_id | string | ✅ | 会话 ID，同会话保持 Memory |
| user_id | string | ✅ | 客户系统用户 ID |
| channel | string | ❌ | web / app / api，默认 web |
| metadata | object | ❌ | 扩展字段 |

**Response 200 — 正常回复**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "response": "您的工单 T-20260601-001 当前状态为「处理中」，预计今日 18:00 前更新。",
    "trace_id": "tr_abc123def456",
    "blocked": false,
    "skills_invoked": ["intent-classify", "agent-route", "ticket-query"],
    "memory_injected": ["working", "episodic"],
    "sources": [],
    "ticket_id": "T-20260601-001",
    "confidence": {
      "intent": 0.92,
      "overall": 0.88
    }
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response 200 — Guardrail 拦截**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "response": "请勿在对话中发送密码、身份证号等敏感信息。",
    "trace_id": "tr_blocked001",
    "blocked": true,
    "skills_invoked": [],
    "memory_injected": [],
    "sources": [],
    "block_reason": "sensitive_data"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response 200 — RAG 带引用**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "response": "企业版包含无限工单、专属客户经理和 99.9% SLA。[1]",
    "trace_id": "tr_rag001",
    "blocked": false,
    "skills_invoked": ["intent-classify", "knowledge-retrieve", "answer-compose"],
    "memory_injected": ["working", "semantic"],
    "sources": [
      {
        "ref": "[1]",
        "doc_id": "FAQ-012",
        "title": "企业版套餐说明",
        "url": "https://kb.customer.com/docs/FAQ-012",
        "score": 0.89
      }
    ],
    "confidence": { "intent": 0.95, "rag": 0.89 }
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2.2 GET `/traces/{trace_id}` — 查询 Trace

**描述**：运营/IT 按 trace_id 查询完整 Harness 调用链（权限：`ops:read`）。

**Response 200**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "trace_id": "tr_abc123def456",
    "session_id": "sess_8f3a2b1c",
    "user_id": "user_10086",
    "started_at": "2026-06-01T08:15:30Z",
    "duration_ms": 1240,
    "skills_invoked": ["intent-classify", "ticket-query"],
    "memory_injected": ["working", "episodic"],
    "attribution": "",
    "steps": [
      {
        "name": "input_guardrail",
        "layer": "guardrail",
        "duration_ms": 2,
        "output_summary": "passed"
      },
      {
        "name": "memory_injector",
        "layer": "memory",
        "duration_ms": 45,
        "metadata": { "layers": ["working", "episodic"] }
      },
      {
        "name": "skill:ticket-query",
        "layer": "skill",
        "duration_ms": 890,
        "metadata": { "skill_id": "ticket-query", "version": "1.0.0" }
      }
    ]
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 3. 客户系统回调接口（AgentOps → 客户）

> 以下为客户侧需实现的接口，AgentOps 通过 Tool 层调用。

### 3.1 POST `{customer}/api/tickets` — 创建工单

**AgentOps 请求**

```json
{
  "title": "服务器宕机",
  "priority": "urgent",
  "category": "repair",
  "customer_id": "C-1001",
  "description": "用户反馈生产环境服务器无法访问，已持续 2 小时。",
  "source": "agentops",
  "trace_id": "tr_abc123"
}
```

**客户系统响应 201**

```json
{
  "id": "T-20260601-001",
  "status": "new",
  "created_at": "2026-06-01T08:16:00Z",
  "assignee": null
}
```

### 3.2 GET `{customer}/api/tickets/{id}` — 查询工单

**客户系统响应 200**

```json
{
  "id": "T-20260601-001",
  "title": "服务器宕机",
  "status": "in_progress",
  "priority": "urgent",
  "created_at": "2026-06-01T08:16:00Z",
  "updated_at": "2026-06-01T10:30:00Z",
  "assignee": { "id": "agent_007", "name": "张工" }
}
```

### 3.3 GET `{customer}/api/customers/{id}` — CRM 查询

**客户系统响应 200**

```json
{
  "id": "C-1001",
  "name": "示例科技有限公司",
  "tier": "vip",
  "contract": "enterprise",
  "preferred_channel": "email",
  "sla_hours": 4
}
```

### 3.4 POST `{customer}/api/escalations` — 转人工

```json
{
  "ticket_id": "T-20260601-001",
  "reason": "user_complaint_high_sentiment",
  "queue": "vip_support",
  "trace_id": "tr_esc001"
}
```

---

## 4. 知识库检索 API（内部 / 客户 KB）

### POST `/internal/kb/search`

```json
{
  "query": "企业版和专业版区别",
  "top_k": 5,
  "min_score": 0.7,
  "filters": { "doc_type": ["faq", "sop"], "status": "published" }
}
```

**Response**

```json
{
  "code": 0,
  "data": {
    "chunks": [
      {
        "doc_id": "FAQ-012",
        "title": "企业版套餐说明",
        "content": "企业版包含...",
        "score": 0.89,
        "url": "https://kb.customer.com/docs/FAQ-012"
      }
    ]
  }
}
```

---

## 5. 运营 API（P1）

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/ops/skills/health` | Skill 健康度 | ops:read |
| GET | `/eval/reports/latest` | 最新评测报告 | ops:read |
| POST | `/eval/run` | 触发评测 | ops:admin |
| GET | `/badcases` | Bad Case 列表 | ops:read |

---

## 6. 限流与 SLA

| 接口 | 限流 | P95 延迟 |
|------|------|----------|
| POST `/chat` | 60 req/min/user | ≤3000ms |
| GET `/traces/*` | 120 req/min | ≤500ms |
| 客户工单 API | 依客户系统 | Agent 侧重试 3 次 |

---

## 7. 联调 checklist（客户 IT）

- [ ] HTTPS 证书与域名就绪
- [ ] JWT 签发与校验对接（或 API Key 过渡期方案）
- [ ] 工单 CRUD 接口权限开通（服务账号 `agentops-svc`）
- [ ] CRM 只读接口开通
- [ ] 知识库导出/检索 API 或批量导入 50+ 文档
- [ ] 转人工队列接口或 Webhook 确认
- [ ] VPC 出站白名单（LLM API、客户内网 API）
- [ ] staging 环境联调通过（≥20 条场景）

---

## 8. 版本兼容

| API 版本 | 状态 | 说明 |
|----------|------|------|
| v1 | 当前 | MVP 交付 |
| v2 | 规划 | SSO、多租户、Webhook 事件 |

Breaking change 提前 **30 天** 书面通知，旧版本并行 **60 天**。
