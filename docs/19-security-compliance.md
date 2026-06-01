# 安全与合规说明

> **文档编号** DOC-AOPS-SEC-001 · **版本** v1.0  
> **受众**：客户 IT（王工）、信息安全审查、采购合规  
> **适用**：智服通 AgentOps MVP 私有化部署

---

## 1. 合规框架

| 框架 | 适用 | 本产品措施 |
|------|------|-----------|
| 《个人信息保护法》 | 用户对话、Profile | PII 脱敏、最小采集 |
| 等保 2.0（三级）参考 | 企业客户 | 访问控制、审计、加密 |
| 客户数据不出境 | 合同约束 | 私有化/VPC，LLM 内网或国内节点 |

---

## 2. 数据分类与处理

| 数据类型 | 示例 | 分类 | 存储 | 加密 |
|----------|------|------|------|------|
| 对话内容 | 用户消息 | 内部/敏感 | Working（短期） | 传输 TLS；静态 AES-256 |
| 会话摘要 | Episodic | 内部 | PostgreSQL 90d | 静态加密 |
| 客户 Profile | VIP 等级 | 内部 | PostgreSQL | 静态加密 |
| Trace | Skill 调用链 | 内部 | PostgreSQL 180d | 含审计 |
| 工单 ID | T-xxx | 业务 | 引用客户系统 | — |
| PII | 手机/身份证 | **敏感** | **不持久化原文** | Guardrail 拦截 |

### 2.1 Memory Write Policy

- Working → Episodic：**摘要后写入**，原文不落库  
- 自动 **PII 检测**（手机、身份证、银行卡）→ 替换为 `[REDACTED]`  
- 用户可请求 **删除** Episodic（Forget Policy，30 天内完成）

---

## 3. 访问控制

| 控制 | 实现 |
|------|------|
| 认证 | JWT（客户 IdP / OIDC 二期） |
| 授权 | RBAC（见 PRD §10、[04-permission](./04-permission-and-data-flow.md)） |
| 服务账号 | `agentops-svc` 最小权限调用工单/CRM |
| 管理后台 | 仅内网/VPN + MFA（客户 IdP） |
| API 密钥 | Secret Manager，90 天轮换 |

---

## 4. 传输与存储安全

| 层 | 措施 |
|----|------|
| 传输 | TLS 1.2+；HSTS；禁用弱 cipher |
| 存储 | PostgreSQL TDE 或磁盘加密；Redis AUTH |
| 密钥 | KMS 管理；不入 Git |
| 日志 | 禁止记录完整 message 原文（可配置采样脱敏） |

---

## 5. Agent 特有安全

### 5.1 Prompt 注入防护

- Input Guardrail 规则 + 模式库（可客户扩展）  
- 系统 Prompt 与用户输入 **分隔**（Structured prompt）  
- Tool 参数 **Schema 校验**，禁止 LLM 自由构造 SQL/命令

### 5.2 输出安全

- Output Guardrail：敏感信息泄露检测  
- RAG 场景 **强制 source_refs**，降低幻觉风险  
- 禁止 LLM 直接输出退款金额、状态变更确认（规则引擎生成）

### 5.3 LLM 数据

| 项 | 策略 |
|----|------|
| 训练数据 | **不使用**客户对话训练（合同 DPA） |
| 日志上传 | 默认关闭；若启用需客户书面同意 |
| 模型部署 | 优先客户指定内网模型 / 国内云 |

---

## 6. 审计

| 事件 | 记录内容 | 保留 |
|------|----------|------|
| 登录/鉴权失败 | user_id, ip, time | 1 年 |
| Skill/Prompt 变更 | 版本, 操作人, diff | 永久 |
| 工单 Tool 调用 | ticket_id, trace_id | 180 天 |
| Guardrail 拦截 | reason, hash(message) | 180 天 |
| Memory 删除请求 | user_id, time | 1 年 |

审计日志 **append-only**，IT 可导出至 SIEM。

---

## 7. 漏洞与应急响应

| 流程 | SLA |
|------|-----|
| 漏洞报告渠道 | security@vendor.com |
| 确认响应 | 24h |
| Critical 补丁 | 72h 内提供方案 |
| 事件通知客户 | 发现后 24h 内 |

---

## 8. 第三方依赖

| 依赖 | 用途 | 数据共享 | 备选 |
|------|------|----------|------|
| LLM API | 推理 | 对话片段（可内网） | 客户指定模型 |
| 向量库 | RAG | 知识库文档 | 自建 Qdrant |
| 客户工单 API | 业务 | 工单字段 | — |

---

## 9. 安全审查 Checklist（王工）

- [ ] 数据流图与存储位置确认（[04-permission](./04-permission-and-data-flow.md)）
- [ ] VPC 网络隔离与出站白名单
- [ ] JWT/SSO 集成方案确认
- [ ] PII 处理与 Memory Policy 确认
- [ ] 审计日志满足内控要求
- [ ] 渗透测试报告（交付前或试运行后）
- [ ] DPA / 数据处理附录签署

---

## 10. 签字

| 角色 | 姓名 | 结论 | 日期 |
|------|------|------|------|
| 客户 IT 安全 | 王工 | □通过 □有条件 □不通过 | |
| 供应商安全 | | | |

**有条件通过附加条件**：

1. _________________________________________________
