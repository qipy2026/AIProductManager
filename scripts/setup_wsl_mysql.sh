#!/usr/bin/env bash
# WSL MySQL 初始化 — agentops 库 + 专用账号
set -euo pipefail

DB=agentops
USER=agentops
PASS="${AGENTOPS_MYSQL_PASS:-Agentops@2026!}"

DEBIAN_CNF="/etc/mysql/debian.cnf"
if [[ ! -f "$DEBIAN_CNF" ]]; then
  echo "错误: 未找到 $DEBIAN_CNF，请确认 WSL 已安装 MySQL"
  exit 1
fi

echo ">>> 创建数据库 $DB 与用户 $USER ..."

mysql --defaults-file="$DEBIAN_CNF" <<SQL
CREATE DATABASE IF NOT EXISTS ${DB} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${USER}'@'%' IDENTIFIED BY '${PASS}';
CREATE USER IF NOT EXISTS '${USER}'@'localhost' IDENTIFIED BY '${PASS}';
GRANT ALL PRIVILEGES ON ${DB}.* TO '${USER}'@'%';
GRANT ALL PRIVILEGES ON ${DB}.* TO '${USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo ">>> 验证 agentops 账号"
mysql -u "$USER" -p"$PASS" -h 127.0.0.1 -e "USE ${DB}; SELECT 'OK' AS status;"

echo ""
echo "完成。"
echo "  用户: $USER"
echo "  密码: $PASS"
echo "  库名: $DB"
echo ""
echo "Windows 启动: .\\scripts\\start_backend_mysql.ps1"
