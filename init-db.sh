#!/bin/bash
set -e

echo "开始导入数据库dump文件..."

# 等待PostgreSQL完全启动
until pg_isready -U postgres; do
  echo "等待PostgreSQL启动..."
  sleep 2
done

# 导入dump文件
if [ -f /docker-entrypoint-initdb.d/kgjdemodb_1028.dump ]; then
    echo "正在导入 kgjdemodb_1028.dump..."
    # 使用 pg_restore 导入自定义格式的dump文件
    pg_restore -U postgres -d kgjdemodb --verbose --no-owner --no-acl /docker-entrypoint-initdb.d/kgjdemodb_1028.dump
    echo "数据库导入完成!"
else
    echo "警告: 找不到dump文件"
fi

