#!/usr/bin/env python3
"""
测试游赚模块启动脚本
"""

import uvicorn
from module_yozuan.app import yozuan_app

if __name__ == "__main__":
    print("🚀 启动游赚模块测试服务器...")
    print("📖 API文档地址: http://localhost:8001/docs")
    print("🔍 OpenAPI规范: http://localhost:8001/openapi.json")
    print("📊 ReDoc文档: http://localhost:8001/redoc")
    print("ℹ️  模块信息: http://localhost:8001/info")
    print("💚 健康检查: http://localhost:8001/health")
    print("⚙️  配置信息: http://localhost:8001/config")
    print("=" * 60)
    
    uvicorn.run(
        yozuan_app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
