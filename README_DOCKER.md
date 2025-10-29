# Docker 部署说明

本项目使用 Docker 和 Docker Compose 进行部署，包含 Flask 应用和 PostgreSQL 数据库。

## 前提条件

- 已安装 Docker
- 已安装 Docker Compose

## 快速启动

### 1. 构建并启动所有服务

```bash
docker-compose up -d --build
```

### 2. 查看服务状态

```bash
docker-compose ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看Flask应用日志
docker-compose logs -f flask_app

# 只查看数据库日志
docker-compose logs -f postgres
```

## 访问应用

- Flask API: http://localhost:5000
- PostgreSQL: localhost:5432

### API端点示例

- http://localhost:5000/api/postgres/log_app/pcap_label_stats
- http://localhost:5000/api/postgres/traffic_log/summary_stats
- http://localhost:5000/api/postgres/traffic_log/time_stats
- http://localhost:5000/api/postgres/traffic_log/malicious_traffic

## 常用命令

### 停止服务

```bash
docker-compose down
```

### 停止服务并删除数据卷（清除所有数据）

```bash
docker-compose down -v
```

### 重启服务

```bash
docker-compose restart
```

### 只重启Flask应用

```bash
docker-compose restart flask_app
```

### 进入容器内部

```bash
# 进入Flask应用容器
docker-compose exec flask_app bash

# 进入PostgreSQL容器
docker-compose exec postgres bash
```

### 手动导入数据库（如果自动导入失败）

```bash
# 方法1: 使用docker-compose
docker-compose exec -T postgres psql -U postgres -d kgjdemodb < kgjdemodb_xgs.dump

# 方法2: 进入容器后导入
docker-compose exec postgres bash
psql -U postgres -d kgjdemodb < /docker-entrypoint-initdb.d/kgjdemodb_xgs.dump
```

### 连接到PostgreSQL数据库

```bash
docker-compose exec postgres psql -U postgres -d kgjdemodb
```

## 配置说明

### 数据库配置

默认配置在 `docker-compose.yml` 中：
- 数据库名: kgjdemodb
- 用户名: postgres
- 密码: postgres123
- 端口: 5432

如需修改，请编辑 `docker-compose.yml` 文件中的环境变量。

### Flask应用配置

Flask应用通过环境变量配置数据库连接，这些变量在 `docker-compose.yml` 中定义。

## 故障排除

### 1. 数据库连接失败

检查PostgreSQL是否已完全启动：
```bash
docker-compose logs postgres
```

### 2. 数据未导入

手动导入数据：
```bash
docker-compose exec -T postgres psql -U postgres -d kgjdemodb < kgjdemodb_xgs.dump
```

### 3. 端口冲突

如果5000或5432端口被占用，请修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "自定义端口:5000"  # Flask应用
  - "自定义端口:5432"  # PostgreSQL
```

### 4. 重新构建镜像

如果修改了代码或依赖，需要重新构建：
```bash
docker-compose down
docker-compose up -d --build
```

## 目录结构

```
.
├── app/                    # Flask应用目录
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   └── postgres_api/      # API路由
├── Dockerfile             # Flask应用Docker镜像
├── docker-compose.yml     # Docker编排配置
├── requirements.txt       # Python依赖
├── run.py                 # 应用入口
├── init-db.sh            # 数据库初始化脚本
└── kgjdemodb_xgs.dump    # 数据库备份文件
```

## 注意事项

1. 首次启动会自动导入 `kgjdemodb_xgs.dump` 数据
2. 数据持久化在Docker卷 `postgres_data` 中
3. 如需清空数据重新导入，使用 `docker-compose down -v` 删除数据卷后重新启动
4. 生产环境建议修改默认密码

