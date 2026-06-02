# 在线 Demo 与投递指南

> **目标**：5 分钟内让面试官/客户「能点、能看、能信」—— 对应 JD「Vibe Coding 可演示原型」。

---

## 1. 一键本地 Demo（推荐）

```bash
# 克隆后于项目根目录
docker compose up --build
```

| 服务 | 地址 |
|------|------|
| **前端** | http://localhost:3000 |
| **后端 API** | http://localhost:8000/docs |
| **MySQL** | localhost:3306 |

前端环境变量已指向 `BACKEND_URL=http://backend:8000`。

### Windows 快速路径（已有 MySQL）

```powershell
.\scripts\start_backend_mysql.ps1   # 终端 1 · 端口 8002
cd frontend
$env:BACKEND_URL="http://localhost:8002"
npm run dev                          # 终端 2 · 端口 3000
```

---

## 2. 5 分钟演示动线（录屏 / 现场）

| 顺序 | 页面 | 操作 | 讲什么（JD 对标） |
|------|------|------|-------------------|
| 1 | `/chat` | 「企业版和专业版区别？」 | RAG + 来源引用 |
| 2 | `/chat` | 「服务器宕机请处理」 | Skill 建单 ticket-create |
| 3 | `/chat` | 「查 T-001 进度」 | Skill 边界 ticket-query |
| 4 | `/tickets` | 展开工单行 | 对话与工单分离 |
| 5 | `/ops` → **业务 ROI** | 看基线 vs 当前 | **可量化业务结果** |
| 6 | `/ops` → Bad Case | 载入七层演示 | 归因 → Trace |
| 7 | `/eval` | 运行全量评测 | 120 条门禁 ≥85% |

详细分镜：[scripts/record_demo.md](../scripts/record_demo.md)

---

## 3. 录屏产出

```powershell
# 自动打开演示页面 + 打印旁白提示
.\scripts\record_demo.ps1

# 或使用 Playwright 有头模式
cd e2e && npm install && npx playwright install chromium && npm run test:headed
```

**投递文件**：将录屏保存为 `assets/demo.mp4`（5 分钟以内）。

---

## 4. 云部署（可选）

| 平台 | 组件 | 说明 |
|------|------|------|
| **Railway / Render** | `Dockerfile` backend | 环境变量见 `.env.example` |
| **Vercel** | `frontend/` | 设置 `BACKEND_URL` 指向已部署 API |
| **Docker Compose** | 全栈 | 面试现场最稳 |

部署后在 README「在线 Demo」一节填入你的 URL，例如：

```markdown
## 在线 Demo
- 产品：https://your-app.vercel.app
- 录屏：assets/demo.mp4
```

---

## 5. 投递三件套检查清单

- [ ] **可点击**：本地或在线 URL 可访问 `/chat` `/ops` `/eval`
- [ ] **能讲 ROI**：`/ops` → 业务 ROI Tab + [09-roi-report-sample.md](./09-roi-report-sample.md)
- [ ] **有录屏**：`assets/demo.mp4` 或 B 站/飞书链接写在 README

---

## 6. 相关文档

| 文档 | 用途 |
|------|------|
| [JD.md](../JD.md) | 岗位对标 |
| [09-roi-report-sample.md](./09-roi-report-sample.md) | VP 汇报样例 |
| [07-co-creation-workshop-kit.md](./07-co-creation-workshop-kit.md) | 客户共创 |
| [08-requirement-discovery-case.md](./08-requirement-discovery-case.md) | 需求挖掘案例 |
