# Docker 指南
---

## 📚 第1步：为什么需要 Docker？(解决 “我电脑上能跑” 的问题)

作为前端，你肯定遇到过：
- 新同事 clone 项目，`node` 版本不对，装不上依赖。
- `node-sass` 在 Windows 和 Mac 上编译结果不同。
- `npm install` 后，`node_modules` 巨大无比，还可能因为系统不同有差异。

**Docker 就是用来解决这些问题的。** 它能创建一个**标准化的、可重复的、与你电脑系统隔离**的运行环境。

---

## 📦 第2步：核心概念 (Dockerfile, 镜像, 容器)

#### 2.1 `Dockerfile` - 环境的 “配方”

`Dockerfile` 是一个文本文件，里面写了一步步的指令，告诉 Docker 如何打包你的应用环境。

**前端类比**：你可以把它想象成 `package.json` + `webpack.config.js` 的组合。
- `package.json` 定义了需要哪些依赖 (`npm install`)。
- `webpack.config.js` 定义了如何构建 (`npm run build`)。

让我们逐行看我们项目里的 `Dockerfile`：

```dockerfile
# 1. 基础环境：指定 Node 版本
# FROM node:18-alpine
FROM python:3.11-slim  # 我们的项目用 Python，所以指定 Python 3.11

# 2. 设置工作目录：类似 cd /path/to/project
WORKDIR /app

# 3. 安装系统依赖：类似用 apt-get 装一些全局工具
# RUN npm install -g some-cli-tool
RUN sed -i '...' /etc/apt/sources.list # 更换国内镜像源，加速下载
RUN apt-get update && apt-get install -y gcc postgresql-client # 安装编译工具和 psql 客户端

# 4. 复制并安装项目依赖：相当于 npm install
COPY requirements.txt .
RUN pip install -r requirements.txt -i ... # 从清华源安装依赖

# 5. 复制项目代码
COPY . .

# 6. 暴露端口：告诉外界这个环境里的应用会监听 5000 端口
EXPOSE 5000

# 7. 启动命令：相当于 package.json 里的 "scripts": {"start": "node index.js"}
CMD ["python", "run.py"]
```

#### 2.2 `镜像 (Image)` - 打包好的 “安装包”

当你运行 `docker build` (或者 `docker-compose build`) 时，Docker 会按照 `Dockerfile` 的指令一步步执行，最终生成一个**只读的**镜像。

**前端类比**：镜像就好像你运行 `npm run build` 后生成的 `dist` 或 `build` 文件夹。
- 它包含了所有运行需要的东西（代码、依赖、环境）。
- 它是静态的、不可变的。
- 你可以把它推送到仓库 (Docker Hub)，别人可以拉下来直接用，保证环境完全一致。

#### 2.3 `容器 (Container)` - 运行中的 “程序实例”

镜像是静态的，而容器是**镜像运行起来的实例**。

**前端类比**：容器就是你运行 `npm run serve` 或 `node dist/server.js` 时的那个**正在运行的进程**。
- 镜像是 “菜谱”，容器是根据菜谱做出来的 “菜”。
- 你可以从同一个镜像启动多个容器，就像你可以开多个终端运行多次 `npm run serve` 一样。
- 每个容器都是相互隔离的。

---

## 🚀 第3步：`docker-compose.yml` - “总指挥”

一个现代项目通常不止一个服务（比如前端 + 后端 + 数据库）。如果每个服务都手动 `docker run`，会非常麻烦。

`docker-compose` 就是用来**编排和管理多个容器**的工具。

**前端类比**：`docker-compose.yml` 就像一个超级 `package.json` 的 `scripts`，你可以用一个命令（`docker-compose up`）同时启动前端开发服务器、后端 API 服务、Mock 服务器，并让它们能相互通信。

让我们逐行看我们项目里的 `docker-compose.yml`：

```yaml
# 定义所有服务
services:
  
  # --- 服务1：PostgreSQL 数据库 ---
  postgres:
    image: postgres:15-alpine  # 直接使用官方做好的镜像，而不是自己 build
    container_name: postgres_db # 给容器起个名字
    restart: "no" # 电脑重启后不自动启动
    
    # 环境变量：相当于给容器用的 .env 文件
    environment:
      POSTGRES_DB: kgjdemodb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      
    # 端口映射：<宿主机端口>:<容器端口>
    # 把你电脑的 5432 端口连接到容器的 5432 端口，这样你就能在本地连接数据库了
    ports:
      - "5432:5432"
      
    # 数据卷 (Volumes)：这是 Docker 最重要的概念之一！
    volumes:
      # 1. 命名卷：用于持久化数据
      # 把数据库产生的数据存到 postgres_data 这个“硬盘”里，
      # 这样即使容器被删除，数据也不会丢失。
      - postgres_data:/var/lib/postgresql/data
      
      # 2. 绑定挂载：用于初始化
      # 把本地的 dump 文件挂载到容器的初始化目录里
      - ./kgjdemodb_1028.dump:/docker-entrypoint-initdb.d/kgjdemodb_1028.dump
      - ./init-db.sh:/docker-entrypoint-initdb.d/init-db.sh

  # --- 服务2：Flask 后端应用 ---
  flask_app:
    # 从当前目录的 Dockerfile 构建镜像
    build: .
    container_name: flask_app
    
    # 依赖关系：先等 postgres 启动并健康后，再启动 flask_app
    depends_on:
      postgres:
        condition: service_healthy
        
    # 数据卷 (Volumes)：实现代码热更新！
    volumes:
      # 把当前整个项目目录（.）挂载到容器的 /app 目录
      # 你在本地修改任何 .py 文件，容器里会立刻同步变化！
      # 这就是为什么我们改代码不需要重新构建镜像的原因。
      - .:/app

# --- 全局定义 ---

# 定义数据卷“硬盘”
volumes:
  postgres_data:

# 定义网络
networks:
  app_network:
```

---

## 🌐 第4步：网络 (Networks) - 容器间的沟通桥梁

`docker-compose` 会自动创建一个网络（我们这里叫 `app_network`）。

在这个网络里的容器，可以通过**服务名**作为主机名（hostname）来相互访问。

在我们的项目里：
- `flask_app` 的代码里连接数据库的 `host` 是 `postgres`。
- Docker 会把 `postgres` 这个名字解析成 `postgres` 容器的内部 IP 地址。

**前端类比**：就像你在前端代码里 `fetch('/api/users')`，Webpack Dev Server 会自动帮你代理到 `localhost:3000` 的后端服务一样。Docker 网络帮你做了类似的事情。

---

## ✨ 第5步：把所有知识串起来 - `docker-compose up -d --build` 到底做了什么？

`docker-compose` 的执行非常智能，分为并行的“准备阶段”和按依赖顺序执行的“启动阶段”。下面是详细的分解步骤：

### 阶段一：解析与准备 (并行执行)

1.  **解析 `docker-compose.yml`**: Compose 读取文件，制定出一个包含所有服务、网络、数据卷和依赖关系的“作战计划”。

2.  **并行准备资源**:
    -   **任务 A (构建镜像):** 看到 `flask_app` 服务有 `build: .`，于是它去找当前目录的 `Dockerfile`，并开始一步步构建镜像。
    -   **任务 B (拉取镜像):** 同时，看到 `postgres` 服务有 `image: postgres:15-alpine`，就开始从 Docker Hub 拉取这个官方镜像。
    -   **任务 C (创建网络和卷):** 同时，根据文件底部的定义，创建 `app_network` 网络和 `postgres_data` 数据卷。
    -   *注意：`docker-compose.yml` 中服务的书写顺序不影响此阶段的执行顺序，Compose 会尽可能并行以提高效率。*

### 阶段二：启动容器 (严格按 `depends_on` 顺序)

3.  **启动 `postgres` 容器**:
    -   所有准备工作完成后，Compose 检查依赖关系。`flask_app` 依赖 `postgres`，所以必须先启动 `postgres`。
    -   基于下载好的 `postgres:15-alpine` **镜像**启动一个**容器**。
    -   **挂载数据卷和文件**:
        -   将 `postgres_data` 卷挂载到容器的 `/var/lib/postgresql/data` 目录，用于持久化存储数据。
        -   将本地的 `init-db.sh` 和 `kgjdemodb_1028.dump` 文件挂载到容器的 `/docker-entrypoint-initdb.d/` 目录。
    -   **执行初始化 (仅首次)**: 容器第一次启动时，发现数据目录是空的，于是自动执行 `/docker-entrypoint-initdb.d/` 目录下的 `init-db.sh` 脚本，导入数据库 dump 文件。
    -   **映射端口**: 将容器的 `5432` 端口映射到你电脑的 `5432` 端口。
    -   **健康检查**: 启动后，Compose 开始监控 `postgres` 容器的健康状态。

4.  **启动 `flask_app` 容器**:
    -   `depends_on` 检测到 `postgres` 容器的状态变为 `healthy`。
    -   基于构建好的 `shujuku-flask_app` **镜像**启动一个**容器**。
    -   **挂载数据卷 (实现热更新)**:
        -   将本地当前目录 `.` 挂载到容器的 `/app` 目录。这意味着你在本地修改任何 `.py` 文件，容器内都会实时同步，无需重新构建。
    -   **设置环境变量**: 将 `docker-compose.yml` 中定义的环境变量（如 `DB_HOST=postgres`）注入容器。
    -   **连接网络**: 将容器连接到 `app_network` 网络，这样它就可以通过主机名 `postgres` 访问数据库了。
    -   **执行启动命令**: 运行 `Dockerfile` 中定义的 `CMD ["python", "run.py"]` 命令。
    -   **映射端口**: 将容器的 `5000` 端口映射到你电脑的 `5000` 端口。

5.  **完成**:
    -   所有容器都在后台成功运行。你可以通过 `localhost:5000` 访问 Flask API，通过 `localhost:5432` 连接数据库。

---

## 🎯 总结：给前端工程师的 Docker 口诀

- **`Dockerfile`** = 环境定义 (`package.json` + 构建脚本)
- **`Image`** = 打包产物 (`dist` 目录)
- **`Container`** = 运行实例 (`npm run serve` 进程)
- **`docker-compose.yml`** = 多服务总指挥 (同时启动前后端+数据库)
- **`volumes: .:/app`** = 代码热更新 (神器！)
- **`volumes: name:/path`** = 数据持久化 (数据库数据不丢失)
- **`ports: host:container`** = 端口映射 (让你在本地访问)
- **`networks`** = 服务间通信 (让前端容器能 `fetch` 后端容器)

希望这份文档能对你有所帮助！

## 💾 第6步：深入理解 `volumes` (三处 volumes 的区别)

`volumes` 是 Docker 中最核心也最容易混淆的概念之一。你可以把它想象成在你**本地电脑（宿主机）** 和**容器内部**之间建立的一个**同步文件夹**。

在我们的 `docker-compose.yml` 中，`volumes` 出现在了三个不同的地方，各有其用途：

---

### 📍 第一处：PostgreSQL 服务下的 `volumes` (持久化 + 初始化)

```yaml
services:
  postgres:
    volumes:
      # 类型1: 命名卷 (Named Volume) -> 持久化数据
      - postgres_data:/var/lib/postgresql/data
      
      # 类型2: 绑定挂载 (Bind Mount) -> 提供初始化文件
      - ./init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
```

这里包含了两种不同类型的 `volumes`：

#### 1. `postgres_data:/var/lib/postgresql/data` (命名卷)

-   **格式**: `<卷名>:<容器内路径>`
-   **目的**: **持久化数据**，防止数据丢失。
-   **前端类比**: 这就像**浏览器的 `localStorage`**。它的生命周期独立于容器，即使容器被删除 (`docker-compose down`)，这个 `localStorage`（`postgres_data`）**依然存在**。下次启动新容器时，会重新链接到它，数据完好无损。
-   **工作原理**: 将 PostgreSQL 存放数据的文件夹 (`/var/lib/postgresql/data`) 链接到 Docker 管理的一个特殊“硬盘”（名为 `postgres_data`）上。

#### 2. `./init-db.sh:...` (绑定挂载)

-   **格式**: `<本地路径>:<容器内路径>`
-   **目的**: **共享配置文件、代码或初始化脚本**。
-   **前端类比**: 这就像你在项目里有一个 `mock` 数据文件夹。你希望容器在启动时能读取到这些本地文件。
-   **工作原理**: 将本地的 `init-db.sh` 文件**实时映射**到 `postgres` 容器的 `/docker-entrypoint-initdb.d/` 目录里，容器启动时会执行这个目录下的脚本。

---

### 📍 第二处：Flask 服务下的 `volumes` (代码热更新)

```yaml
services:
  flask_app:
    volumes:
      # 类型2: 绑定挂载 (Bind Mount)
      - .:/app
```

-   **格式**: `<本地路径>:<容器内路径>`
-   **目的**: **实现代码实时同步和热更新**。
-   **前端类比**: 这完全就是 **Webpack Dev Server 或 Vite 的核心功能**！
-   **工作原理**: 将你本地的**整个项目文件夹** (`.`) **实时映射**到 `flask_app` 容器的 `/app` 文件夹。你在本地修改任何 `.py` 文件，容器内都会立刻同步变化。因为 Flask 运行在 `debug=True` 模式下，它会检测到文件变化并自动重新加载，实现了热更新，**无需重新构建或重启**。

---

### 📍 第三处：根级别的 `volumes` (声明命名卷)

```yaml
volumes:
  postgres_data:
```

-   **目的**: **正式声明**上面 `postgres` 服务里用到的那个**命名卷**。
-   **前端类比**: 这就像在 JavaScript 文件顶部写 `let myVariable;` 来声明一个变量。
-   **工作原理**: 这是 `docker-compose.yml` 的一个语法要求。所有在服务中使用的命名卷，都必须在根级别的 `volumes` 块中声明，这样 Docker Compose 才知道要创建和管理这个“硬盘”。

---

### 📊 总结与对比

| 位置 | 类型 | 格式 | 目的 | 前端类比 | 是否持久化 |
|---|---|---|---|---|---|
| **`postgres` 服务** | **命名卷** | `卷名:路径` | **持久化数据** | **`localStorage`** | ✅ 是 |
| **`postgres` 服务** | **绑定挂载** | `本地路径:路径` | **初始化脚本** | **`mock` 数据文件** | ❌ 否 (源在本地) |
| **`flask_app` 服务** | **绑定挂载** | `本地路径:路径` | **代码热更新** | **Webpack Dev Server** | ❌ 否 (源在本地) |
| **根级别** | **声明** | `卷名:` | **创建命名卷** | **`let myVariable;`** | - |

希望这次拆解能让你彻底明白这三处 `volumes` 的不同作用和核心思想！
