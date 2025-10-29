# Docker 部署说明

本项目使用 Docker 和 Docker Compose 进行部署，包含 Flask 应用和 PostgreSQL 数据库。

## 前提条件

- 已安装 Docker Desktop
- 已安装 Docker Compose
- **重要**：建议配置 Docker 镜像加速器（国内环境必需）

## 快速启动

### 0. 配置 Docker 镜像加速器（首次使用必须）

**在国内环境下，必须先配置镜像加速器，否则无法下载镜像！**

打开 Docker Desktop → 设置 → Docker Engine，添加以下配置：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

点击 "Apply & Restart"，等待 Docker 重启完成。

### 1. 构建并启动所有服务

```bash
docker-compose up -d --build
```

首次启动会自动：
- 下载并构建镜像（使用国内镜像源加速）
- 创建数据库
- 自动导入 `kgjdemodb_1028.dump` 数据文件

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

**注意**：当前使用的是 PostgreSQL 自定义格式的 dump 文件，需要使用 `pg_restore` 命令。

```bash
# 方法1: 从宿主机导入
docker-compose exec -T postgres pg_restore -U postgres -d kgjdemodb --verbose --no-owner --no-acl < kgjdemodb_1028.dump

# 方法2: 进入容器后导入
docker-compose exec postgres bash
pg_restore -U postgres -d kgjdemodb --verbose --no-owner --no-acl /docker-entrypoint-initdb.d/kgjdemodb_1028.dump
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

手动导入数据（使用 pg_restore）：
```bash
docker-compose exec -T postgres pg_restore -U postgres -d kgjdemodb --verbose --no-owner --no-acl < kgjdemodb_1028.dump
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

### 5. 更换数据库 dump 文件

如果需要使用新的数据库备份文件：

**步骤：**

1. 修改配置文件：
   - `docker-compose.yml` 中的 dump 文件路径
   - `init-db.sh` 中的文件名

2. 清除旧数据并重新导入：
```bash
# 停止容器并删除数据卷（会清除所有数据！）
docker-compose down -v

# 重新启动（自动导入新数据）
docker-compose up -d

# 查看导入日志
docker-compose logs --tail=50 postgres
```

**注意**：`-v` 参数会删除所有数据，请确保已备份重要数据！

### 6. Docker 镜像加速问题

如果遇到以下错误：
```
failed to fetch oauth token
failed to resolve source metadata
```

说明没有配置镜像加速器，请参考"快速启动"第 0 步配置镜像加速器。

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
└── kgjdemodb_1028.dump   # 数据库备份文件（PostgreSQL 自定义格式）
```

## 注意事项

1. **首次启动会自动导入** `kgjdemodb_1028.dump` 数据（PostgreSQL 自定义格式）
2. **数据持久化**在 Docker 卷 `postgres_data` 中，重启容器不会丢失数据
3. **清空数据重新导入**：使用 `docker-compose down -v` 删除数据卷后重新启动
4. **生产环境**：建议修改默认密码（postgres123）
5. **国内环境**：必须配置 Docker 镜像加速器，否则无法下载镜像
6. **init-db.sh** 只在数据库首次初始化时执行一次
7. **dump 文件格式**：
   - `.sql` 文件使用 `psql` 导入
   - `.dump` 文件使用 `pg_restore` 导入

## 常见问题

### Q1: 为什么重启容器后数据还在？

因为数据存储在 Docker 数据卷中，只有使用 `docker-compose down -v` 才会删除。

### Q2: 如何更新代码？

修改代码后，只需重启 Flask 容器：
```bash
docker-compose restart flask_app
```

如果修改了 `requirements.txt` 或 `Dockerfile`，需要重新构建：
```bash
docker-compose up -d --build
```

### Q3: 如何查看数据库中的表？

```bash
docker-compose exec postgres psql -U postgres -d kgjdemodb -c "\dt"
```

### Q4: 容器一直重启怎么办？

查看错误日志：
```bash
docker-compose logs flask_app
docker-compose logs postgres
```

常见原因：
- 数据库连接失败（检查 `DB_HOST`, `DB_PASSWORD` 等配置）
- 代码有语法错误
- 端口被占用

### Q5: 如何备份数据库？

```bash
# 导出为自定义格式
docker-compose exec postgres pg_dump -U postgres -d kgjdemodb -F c -f /tmp/backup.dump

# 从容器复制到宿主机
docker cp postgres_db:/tmp/backup.dump ./backup_$(date +%Y%m%d).dump
```

