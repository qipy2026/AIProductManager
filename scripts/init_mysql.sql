-- WSL MySQL 初始化
-- mysql -u root -p < scripts/init_mysql.sql

CREATE DATABASE IF NOT EXISTS agentops DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agentops;

-- 表结构由应用 startup 自动 CREATE IF NOT EXISTS
-- 首次启动: OPS_DB=mysql python -m uvicorn backend.main:app --port 8002
