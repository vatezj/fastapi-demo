# 快速开始指南

## 概述

本指南将帮助您快速搭建 RuoYi-FastAPI 开发环境，并运行第一个示例。

## 环境准备

### 1. 安装 Python

确保您的系统已安装 Python 3.8 或更高版本：

```bash
# 检查 Python 版本
python --version
# 或
python3 --version
```

### 2. 安装数据库

#### MySQL 安装
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS (使用 Homebrew)
brew install mysql

# 启动 MySQL 服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### PostgreSQL 安装
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server

# macOS (使用 Homebrew)
brew install postgresql

# 启动 PostgreSQL 服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. 安装 Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis

# macOS (使用 Homebrew)
brew install redis

# 启动 Redis 服务
sudo systemctl start redis
sudo systemctl enable redis
```

## 项目搭建

### 1. 克隆项目

```bash
# 克隆项目到本地
git clone <repository-url>
cd ruoyi-fastapi-backend

# 查看项目结构
ls -la
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; print('FastAPI 安装成功')"
```

### 4. 环境配置

创建 `.env` 文件：

```env
# 应用配置
APP_ENV=dev
APP_NAME=RuoYi-FastAPI
APP_HOST=0.0.0.0
APP_PORT=9099
APP_ROOT_PATH=/dev-api
APP_RELOAD=true

# 数据库配置 (MySQL)
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_DATABASE=ruoyi-fastapi
DB_ECHO=true

# 数据库配置 (PostgreSQL)
# DB_TYPE=postgresql
# DB_HOST=127.0.0.1
# DB_PORT=5432
# DB_USERNAME=postgres
# DB_PASSWORD=your_password
# DB_DATABASE=ruoyi-fastapi

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=
REDIS_DATABASE=2

# JWT配置
JWT_SECRET_KEY=your_secret_key_here_make_it_long_and_random
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
JWT_REDIS_EXPIRE_MINUTES=30
```

### 5. 数据库初始化

#### MySQL 初始化

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE `ruoyi-fastapi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

# 创建用户并授权
CREATE USER 'ruoyi'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON `ruoyi-fastapi`.* TO 'ruoyi'@'%';
FLUSH PRIVILEGES;

# 退出 MySQL
EXIT;

# 导入初始数据
mysql -u ruoyi -p ruoyi-fastapi < sql/ruoyi-fastapi.sql
```

#### PostgreSQL 初始化

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库
CREATE DATABASE "ruoyi-fastapi";

# 创建用户并授权
CREATE USER ruoyi WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE "ruoyi-fastapi" TO ruoyi;

# 退出 PostgreSQL
\q

# 导入初始数据
psql -U ruoyi -d ruoyi-fastapi -f sql/ruoyi-fastapi-pg.sql
```

### 6. 启动应用

```bash
# 启动应用
python app.py
```

应用将在 `http://localhost:9099` 启动。

## 验证安装

### 1. 访问 API 文档

打开浏览器访问：
- Swagger UI: `http://localhost:9099/docs`
- ReDoc: `http://localhost:9099/redoc`

### 2. 测试健康检查

```bash
# 使用 curl 测试
curl http://localhost:9099/dev-api/common/health

# 预期响应
{
    "code": 200,
    "msg": "系统运行正常",
    "data": {
        "status": "UP",
        "timestamp": "2024-01-01T12:00:00"
    }
}
```

### 3. 测试数据库连接

```bash
# 测试数据库连接
curl http://localhost:9099/dev-api/common/db-status

# 预期响应
{
    "code": 200,
    "msg": "数据库连接正常",
    "data": {
        "status": "connected",
        "database": "ruoyi-fastapi"
    }
}
```

## 开发工具配置

### 1. VS Code 配置

安装推荐的扩展：
- Python
- FastAPI
- SQLAlchemy
- Python Docstring Generator

创建 `.vscode/settings.json`：

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

### 2. PyCharm 配置

1. 打开项目
2. 配置 Python 解释器为虚拟环境
3. 安装项目依赖
4. 配置运行配置

## 第一个功能开发

### 1. 创建数据表

```sql
-- 创建示例表
CREATE TABLE `demo_user` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` varchar(50) NOT NULL COMMENT '用户名',
    `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
    `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='示例用户表';
```

### 2. 使用代码生成器

```python
# 在代码生成器中添加表
table_name = "demo_user"
gen_service = GenService()
await gen_service.generate_code(table_name)
```

### 3. 测试新功能

```bash
# 测试用户列表接口
curl http://localhost:9099/dev-api/demo-user/list

# 测试添加用户
curl -X POST http://localhost:9099/dev-api/demo-user \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com"
  }'
```

## 常见问题解决

### 1. 端口被占用

```bash
# 查看端口占用
lsof -i :9099

# 杀死进程
kill -9 <PID>

# 或修改端口
export APP_PORT=9098
```

### 2. 数据库连接失败

```bash
# 检查数据库服务状态
sudo systemctl status mysql
sudo systemctl status postgresql

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-ports
```

### 3. Redis 连接失败

```bash
# 检查 Redis 服务状态
sudo systemctl status redis

# 测试 Redis 连接
redis-cli ping
```

### 4. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 清理缓存
pip cache purge
```

## 下一步

恭喜！您已经成功搭建了 RuoYi-FastAPI 开发环境。接下来可以：

1. 阅读 [架构设计](./ARCHITECTURE.md) 了解系统架构
2. 学习 [API开发](./API_DEVELOPMENT.md) 进行功能开发
3. 参考 [代码生成](./CODE_GENERATION.md) 快速开发新模块
4. 查看 [测试指南](./TESTING_GUIDE.md) 编写测试代码

如有问题，请查看 [常见问题](./FAQ.md) 或提交 Issue。 