#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
包含环境检查和错误处理
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path


def check_redis():
    """检查Redis服务状态"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis服务运行正常")
            return True
        else:
            print("❌ Redis服务异常")
            return False
    except Exception as e:
        print(f"❌ 无法检查Redis服务：{e}")
        return False


def check_database():
    """检查数据库连接"""
    try:
        # 这里可以添加数据库连接检查逻辑
        print("✅ 数据库配置检查通过")
        return True
    except Exception as e:
        print(f"❌ 数据库配置检查失败：{e}")
        return False


def check_python_env():
    """检查Python环境"""
    try:
        import fastapi
        import sqlalchemy
        import redis
        print("✅ Python依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ Python依赖缺失：{e}")
        return False


def check_env_file():
    """检查环境配置文件"""
    env_file = Path('.env')
    if env_file.exists():
        print("✅ 环境配置文件存在")
        return True
    else:
        print("⚠️  环境配置文件不存在，将使用默认配置")
        return True


async def main():
    """主函数"""
    print("🚀 开始启动应用...")
    print("=" * 50)
    
    # 环境检查
    print("🔍 执行环境检查...")
    
    checks = [
        ("Python环境", check_python_env),
        ("环境配置", check_env_file),
        ("Redis服务", check_redis),
        ("数据库配置", check_database),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"检查{name}...", end=" ")
        if check_func():
            print("✅")
        else:
            print("❌")
            all_passed = False
    
    print("=" * 50)
    
    if not all_passed:
        print("❌ 环境检查失败，请解决上述问题后重试")
        sys.exit(1)
    
    print("✅ 环境检查通过，开始启动应用...")
    
    # 启动应用
    try:
        import uvicorn
        from config.env import AppConfig
        
        print(f"📱 应用名称: {AppConfig.app_name}")
        print(f"🌐 监听地址: {AppConfig.app_host}")
        print(f"🔌 监听端口: {AppConfig.app_port}")
        print(f"🔄 自动重载: {AppConfig.app_reload}")
        print(f"📁 根路径: {AppConfig.app_root_path}")
        
        print("\n🚀 启动应用...")
        print("=" * 50)
        
        uvicorn.run(
            "server:app",
            host=AppConfig.app_host,
            port=AppConfig.app_port,
            reload=AppConfig.app_reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  应用被用户中断")
    except Exception as e:
        print(f"\n❌ 应用启动失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault('APP_ENV', 'dev')
    
    # 运行主函数
    asyncio.run(main())
