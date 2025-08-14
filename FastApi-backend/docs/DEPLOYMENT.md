# 部署运维指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的部署和运维方法，包括环境配置、部署方式、监控运维等。

## 部署环境

### 1. 环境要求

```bash
# 系统要求
操作系统: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
Python版本: 3.8+
内存: 最少 2GB，推荐 4GB+
磁盘: 最少 10GB，推荐 50GB+

# 软件依赖
MySQL: 5.7+ / PostgreSQL 10+
Redis: 6.0+
Nginx: 1.18+
```

### 2. 环境配置

#### Python环境配置
```bash
# 安装Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 创建虚拟环境
python3 -m venv /opt/ruoyi-fastapi/venv
source /opt/ruoyi-fastapi/venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 数据库配置
```bash
# MySQL配置
sudo apt install mysql-server
sudo mysql_secure_installation

# 创建数据库和用户
mysql -u root -p
CREATE DATABASE `ruoyi-fastapi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'ruoyi'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON `ruoyi-fastapi`.* TO 'ruoyi'@'%';
FLUSH PRIVILEGES;

# PostgreSQL配置
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE "ruoyi-fastapi";
CREATE USER ruoyi WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE "ruoyi-fastapi" TO ruoyi;
```

#### Redis配置
```bash
# 安装Redis
sudo apt install redis-server

# 配置Redis
sudo nano /etc/redis/redis.conf

# 修改配置
bind 127.0.0.1
port 6379
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru

# 启动Redis
sudo systemctl start redis
sudo systemctl enable redis
```

## 部署方式

### 1. 直接部署

#### 应用配置
```bash
# 创建应用目录
sudo mkdir -p /opt/ruoyi-fastapi
sudo chown -R $USER:$USER /opt/ruoyi-fastapi

# 复制应用文件
cp -r * /opt/ruoyi-fastapi/

# 创建环境配置文件
cat > /opt/ruoyi-fastapi/.env << EOF
APP_ENV=prod
APP_NAME=RuoYi-FastAPI
APP_HOST=0.0.0.0
APP_PORT=9099
APP_ROOT_PATH=/api

DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=ruoyi
DB_PASSWORD=your_password
DB_DATABASE=ruoyi-fastapi

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DATABASE=2

JWT_SECRET_KEY=your_secret_key_here_make_it_long_and_random
JWT_EXPIRE_MINUTES=1440
EOF

# 创建启动脚本
cat > /opt/ruoyi-fastapi/start.sh << 'EOF'
#!/bin/bash
cd /opt/ruoyi-fastapi
source venv/bin/activate
python app.py
EOF

chmod +x /opt/ruoyi-fastapi/start.sh
```

#### 系统服务配置
```bash
# 创建systemd服务文件
sudo cat > /etc/systemd/system/ruoyi-fastapi.service << EOF
[Unit]
Description=RuoYi FastAPI Application
After=network.target mysql.service redis.service

[Service]
Type=simple
User=ruoyi
WorkingDirectory=/opt/ruoyi-fastapi
Environment=PATH=/opt/ruoyi-fastapi/venv/bin
ExecStart=/opt/ruoyi-fastapi/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable ruoyi-fastapi
sudo systemctl start ruoyi-fastapi

# 检查服务状态
sudo systemctl status ruoyi-fastapi
```

### 2. Gunicorn部署

#### Gunicorn配置
```bash
# 安装Gunicorn
pip install gunicorn

# 创建Gunicorn配置文件
cat > /opt/ruoyi-fastapi/gunicorn.conf.py << EOF
# Gunicorn配置文件
bind = "0.0.0.0:9099"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
pidfile = "/opt/ruoyi-fastapi/gunicorn.pid"
accesslog = "/opt/ruoyi-fastapi/logs/gunicorn_access.log"
errorlog = "/opt/ruoyi-fastapi/logs/gunicorn_error.log"
loglevel = "info"
EOF

# 创建启动脚本
cat > /opt/ruoyi-fastapi/start_gunicorn.sh << 'EOF'
#!/bin/bash
cd /opt/ruoyi-fastapi
source venv/bin/activate
gunicorn -c gunicorn.conf.py app:app
EOF

chmod +x /opt/ruoyi-fastapi/start_gunicorn.sh
```

#### 更新systemd服务
```bash
# 更新服务文件
sudo cat > /etc/systemd/system/ruoyi-fastapi.service << EOF
[Unit]
Description=RuoYi FastAPI Application (Gunicorn)
After=network.target mysql.service redis.service

[Service]
Type=simple
User=ruoyi
WorkingDirectory=/opt/ruoyi-fastapi
Environment=PATH=/opt/ruoyi-fastapi/venv/bin
ExecStart=/opt/ruoyi-fastapi/start_gunicorn.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart ruoyi-fastapi
```

### 3. Docker部署

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 9099

# 启动命令
CMD ["python", "app.py"]
```

#### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "9099:9099"
    environment:
      - APP_ENV=prod
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    networks:
      - app-network
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ruoyi-fastapi
      MYSQL_USER: ruoyi
      MYSQL_PASSWORD: your_password
    volumes:
      - mysql-data:/var/lib/mysql
      - ./sql:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7.0
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - app-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - app-network
    restart: unless-stopped

volumes:
  mysql-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

#### 部署命令
```bash
# 构建和启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

## Nginx配置

### 1. 基础配置

```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 上游服务器配置
    upstream ruoyi_fastapi {
        server 127.0.0.1:9099;
        keepalive 32;
    }
    
    # 服务器配置
    server {
        listen 80;
        server_name your_domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your_domain.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # 静态文件
        location /static/ {
            alias /opt/ruoyi-fastapi/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 上传文件
        location /uploads/ {
            alias /opt/ruoyi-fastapi/uploads/;
            expires 1y;
            add_header Cache-Control "public";
        }
        
        # API代理
        location /api/ {
            proxy_pass http://ruoyi_fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时配置
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            
            # 缓冲配置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }
        
        # 健康检查
        location /health {
            proxy_pass http://ruoyi_fastapi/api/common/health;
            access_log off;
        }
        
        # 根路径
        location / {
            return 301 /api/docs;
        }
    }
}
```

### 2. 负载均衡配置

```nginx
# 多实例负载均衡
upstream ruoyi_fastapi {
    server 127.0.0.1:9099 weight=3;
    server 127.0.0.1:9098 weight=2;
    server 127.0.0.1:9097 weight=1;
    
    # 健康检查
    keepalive 32;
}

# 健康检查配置
match health_check {
    status 200;
    header Content-Type = application/json;
}

upstream ruoyi_fastapi {
    server 127.0.0.1:9099 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:9098 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:9097 max_fails=3 fail_timeout=30s;
    
    # 健康检查
    health_check interval=10s fails=3 passes=2 uri=/health match=health_check;
}
```

## 监控运维

### 1. 应用监控

#### 健康检查接口
```python
# 健康检查接口
@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_status = await check_database_health()
        
        # 检查Redis连接
        redis_status = await check_redis_health()
        
        # 检查系统资源
        system_status = await check_system_resources()
        
        if all([db_status, redis_status, system_status]):
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": "healthy",
                    "redis": "healthy",
                    "system": "healthy"
                }
            }
        else:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": "healthy" if db_status else "unhealthy",
                    "redis": "healthy" if redis_status else "unhealthy",
                    "system": "healthy" if system_status else "unhealthy"
                }
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

async def check_database_health() -> bool:
    """检查数据库健康状态"""
    try:
        # 执行简单查询
        result = await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

async def check_redis_health() -> bool:
    """检查Redis健康状态"""
    try:
        await redis.ping()
        return True
    except Exception:
        return False

async def check_system_resources() -> bool:
    """检查系统资源"""
    try:
        # 检查CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 检查内存使用率
        memory = psutil.virtual_memory()
        
        # 检查磁盘使用率
        disk = psutil.disk_usage('/')
        
        # 设置阈值
        if (cpu_percent < 90 and 
            memory.percent < 90 and 
            disk.percent < 90):
            return True
        else:
            return False
    except Exception:
        return False
```

#### 性能监控接口
```python
# 性能监控接口
@router.get("/metrics")
async def get_metrics():
    """获取性能指标"""
    try:
        # 系统指标
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 网络指标
        network = psutil.net_io_counters()
        
        # 进程指标
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_total": disk.total
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "process": {
                "cpu_percent": process_cpu,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms
            }
        }
    except Exception as e:
        return {"error": str(e)}
```

### 2. 日志管理

#### 日志配置
```python
# 日志配置
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 应用日志
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    app_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5,
        encoding="utf-8"
    )
    
    app_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)
    
    # 访问日志
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    
    access_handler = RotatingFileHandler(
        "logs/access.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5,
        encoding="utf-8"
    )
    
    access_formatter = logging.Formatter(
        "%(asctime)s - %(message)s"
    )
    access_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_handler)
    
    # 错误日志
    error_logger = logging.getLogger("error")
    error_logger.setLevel(logging.ERROR)
    
    error_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5,
        encoding="utf-8"
    )
    
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    return app_logger, access_logger, error_logger

# 初始化日志
app_logger, access_logger, error_logger = setup_logging()
```

#### 日志轮转
```bash
# 使用logrotate进行日志轮转
sudo cat > /etc/logrotate.d/ruoyi-fastapi << EOF
/opt/ruoyi-fastapi/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ruoyi ruoyi
    postrotate
        systemctl reload ruoyi-fastapi
    endscript
}
EOF

# 测试配置
sudo logrotate -d /etc/logrotate.d/ruoyi-fastapi
```

### 3. 系统监控

#### 监控脚本
```bash
#!/bin/bash
# 监控脚本 monitor.sh

# 配置
APP_NAME="ruoyi-fastapi"
LOG_FILE="/var/log/monitor.log"
ALERT_EMAIL="admin@example.com"

# 检查应用状态
check_app_status() {
    if ! systemctl is-active --quiet $APP_NAME; then
        echo "$(date): 应用 $APP_NAME 已停止，正在重启..." >> $LOG_FILE
        systemctl restart $APP_NAME
        
        # 发送告警邮件
        echo "应用 $APP_NAME 已停止并重启" | mail -s "应用告警" $ALERT_EMAIL
    fi
}

# 检查端口状态
check_port_status() {
    if ! netstat -tlnp | grep -q ":9099 "; then
        echo "$(date): 端口 9099 未监听，应用可能异常" >> $LOG_FILE
        systemctl restart $APP_NAME
    fi
}

# 检查磁盘空间
check_disk_space() {
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        echo "$(date): 磁盘使用率超过80%: ${DISK_USAGE}%" >> $LOG_FILE
        echo "磁盘使用率过高: ${DISK_USAGE}%" | mail -s "磁盘告警" $ALERT_EMAIL
    fi
}

# 检查内存使用
check_memory_usage() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
        echo "$(date): 内存使用率超过80%: ${MEMORY_USAGE}%" >> $LOG_FILE
        echo "内存使用率过高: ${MEMORY_USAGE}%" | mail -s "内存告警" $ALERT_EMAIL
    fi
}

# 主函数
main() {
    echo "$(date): 开始监控检查" >> $LOG_FILE
    
    check_app_status
    check_port_status
    check_disk_space
    check_memory_usage
    
    echo "$(date): 监控检查完成" >> $LOG_FILE
}

# 执行主函数
main
```

#### 定时监控
```bash
# 添加到crontab
sudo crontab -e

# 每5分钟执行一次监控
*/5 * * * * /opt/ruoyi-fastapi/monitor.sh
```

## 备份策略

### 1. 数据库备份

#### 自动备份脚本
```bash
#!/bin/bash
# 数据库备份脚本 backup.sh

# 配置
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="ruoyi"
DB_PASS="your_password"
DB_NAME="ruoyi-fastapi"
BACKUP_DIR="/opt/backups/database"
BACKUP_RETAIN_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
BACKUP_FILE="$BACKUP_DIR/ruoyi-fastapi-$(date +%Y%m%d_%H%M%S).sql"

# MySQL备份
mysqldump -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASS \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    $DB_NAME > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除过期备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$BACKUP_RETAIN_DAYS -delete

echo "数据库备份完成: $BACKUP_FILE.gz"
```

#### 定时备份
```bash
# 添加到crontab
sudo crontab -e

# 每天凌晨2点执行备份
0 2 * * * /opt/ruoyi-fastapi/backup.sh
```

### 2. 应用备份

#### 应用备份脚本
```bash
#!/bin/bash
# 应用备份脚本 app_backup.sh

# 配置
APP_DIR="/opt/ruoyi-fastapi"
BACKUP_DIR="/opt/backups/application"
BACKUP_RETAIN_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
BACKUP_FILE="$BACKUP_DIR/ruoyi-fastapi-$(date +%Y%m%d_%H%M%S).tar.gz"

# 排除不需要备份的文件
tar --exclude="$APP_DIR/venv" \
    --exclude="$APP_DIR/logs" \
    --exclude="$APP_DIR/__pycache__" \
    --exclude="$APP_DIR/.git" \
    -czf $BACKUP_FILE -C $APP_DIR .

# 删除过期备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +$BACKUP_RETAIN_DAYS -delete

echo "应用备份完成: $BACKUP_FILE"
```

## 故障处理

### 1. 常见问题

#### 应用无法启动
```bash
# 检查服务状态
sudo systemctl status ruoyi-fastapi

# 查看日志
sudo journalctl -u ruoyi-fastapi -f

# 检查端口占用
sudo netstat -tlnp | grep :9099

# 检查配置文件
cat /opt/ruoyi-fastapi/.env

# 手动启动测试
cd /opt/ruoyi-fastapi
source venv/bin/activate
python app.py
```

#### 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查MySQL连接
mysql -u ruoyi -p -h 127.0.0.1

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-ports

# 检查MySQL配置
sudo cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep bind-address
```

#### Redis连接失败
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 检查Redis连接
redis-cli -h 127.0.0.1 -p 6379 ping

# 检查Redis配置
sudo cat /etc/redis/redis.conf | grep bind

# 检查Redis日志
sudo tail -f /var/log/redis/redis-server.log
```

### 2. 性能调优

#### 系统调优
```bash
# 调整文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 调整内核参数
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p

# 调整MySQL配置
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
```

#### 应用调优
```python
# 数据库连接池优化
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
    "echo": False
}

# Redis连接池优化
REDIS_CONFIG = {
    "max_connections": 50,
    "socket_connect_timeout": 5,
    "socket_timeout": 5,
    "retry_on_timeout": True
}

# 异步任务优化
TASK_CONFIG = {
    "max_workers": 10,
    "max_tasks_per_worker": 1000,
    "worker_timeout": 300
}
```

## 最佳实践

### 1. 部署原则
- **环境隔离**: 开发、测试、生产环境严格分离
- **配置管理**: 使用环境变量和配置文件管理配置
- **版本控制**: 所有配置和脚本纳入版本控制
- **自动化**: 尽可能自动化部署和运维流程

### 2. 监控原则
- **全面监控**: 监控应用、系统、网络等各个层面
- **实时告警**: 设置合理的告警阈值和通知机制
- **日志管理**: 完善的日志记录、轮转和归档
- **性能分析**: 定期分析性能指标，及时优化

### 3. 安全原则
- **最小权限**: 应用使用最小必要的系统权限
- **网络安全**: 配置防火墙，限制网络访问
- **数据安全**: 定期备份，加密敏感数据
- **更新维护**: 及时更新系统和依赖包

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 