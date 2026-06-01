# 使用 WSL MySQL 启动后端
$env:OPS_DB = "mysql"
$env:AGENTOPS_STORAGE = "memory"
$env:SEMANTIC_BACKEND = "keyword"
$env:LLM_MODE = "mock"
$env:USE_LANGGRAPH = "0"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "agentops"
$env:MYSQL_PASSWORD = "Agentops@2026!"
$env:MYSQL_DATABASE = "agentops"

Set-Location $PSScriptRoot\..

Write-Host ">>> OPS_DB=mysql MYSQL_HOST=$env:MYSQL_HOST" -ForegroundColor Cyan
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8002
