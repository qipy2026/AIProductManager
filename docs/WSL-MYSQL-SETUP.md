# WSL MySQL 接入指南

## 1. 一次性初始化（WSL）

```bash
# 在 Windows PowerShell 执行
wsl bash /mnt/e/work/aicc/AIProductManager/scripts/setup_wsl_mysql.sh
```

会创建：
- 数据库：`agentops`
- 用户：`agentops` / 密码：`Agentops@2026!`（可通过环境变量 `AGENTOPS_MYSQL_PASS` 自定义）

MySQL 已配置 `bind-address = 0.0.0.0`，Windows 可通过 `127.0.0.1:3306` 访问。

## 2. 启动后端（Windows）

```powershell
.\scripts\start_backend_mysql.ps1
```

或手动：

```powershell
$env:OPS_DB = "mysql"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "agentops"
$env:MYSQL_PASSWORD = "Agentops@2026!"
$env:MYSQL_DATABASE = "agentops"
python -m uvicorn backend.main:app --reload --port 8002
```

前端（另开终端）：

```powershell
cd frontend
$env:BACKEND_URL = "http://localhost:8002"
npm run dev
```

## 3. 验证

```powershell
curl http://localhost:8002/
# 应含 "ops_db": "mysql"

curl http://localhost:8002/api/ops/summary
# trace_count / badcase_count
```

浏览器：
1. `/chat` 发几条消息
2. `/ops` 点「刷新数据」→ 应显示 `存储：mysql`、Trace 条数、Skill 健康度

## 4. WSL 内查看数据

```bash
mysql -u agentops -p'Agentops@2026!' agentops -e "SELECT trace_id, created_at FROM traces ORDER BY created_at DESC LIMIT 5;"
mysql -u agentops -p'Agentops@2026!' agentops -e "SELECT id, attribution, note FROM badcases ORDER BY id DESC LIMIT 5;"
```

## 说明

- `OPS_DB=mysql` 只影响 **运营数据**（Trace / Bad Case）；评测仍可用 `AGENTOPS_STORAGE=memory` 保持确定性。
- 若连不上，确认 WSL MySQL 运行：`wsl sudo service mysql status`
