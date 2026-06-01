# Demo 录屏脚本（5 分钟）

## 前置

```powershell
docker compose up -d backend
# 或
python -m uvicorn backend.main:app --port 8002

cd frontend
$env:BACKEND_URL="http://localhost:8002"
npm run dev
```

## 录屏分镜（按 DEV_TEST_PLAN E2E-001~007）

1. **首页 → /chat**（10s）展示导航与 Trace 区域
2. **E2E-001** 输入「企业版和专业版区别」→ 展示引用来源
3. **E2E-002** 输入「服务器宕机」→ 展示工单号 T-xxx
4. **E2E-003** 输入「查 T-001 进度」→ 展示状态、强调未新建单
5. **E2E-004** 输入「太差了要投诉」→ 展示转人工
6. **E2E-007** 输入「我的密码是abc123」→ 展示 Guardrail
7. **/ops** Skill 健康度 + Trace 查询 + 提交 Bad Case
8. **/eval** 点击「运行评测」→ 展示 120 条通过率

## 自动化录屏（Playwright trace）

```bash
cd e2e
npm install
npx playwright install chromium
npm run test:headed
```

产物：`e2e/test-results/`、`playwright-report/`

## 导出 mp4

使用 OBS / Win+G 屏幕录制，或：

```bash
npx playwright show-trace test-results/.../trace.zip
```

保存为 `assets/demo.mp4` 供作品集投递。
