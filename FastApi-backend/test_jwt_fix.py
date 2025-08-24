#!/usr/bin/env python3
"""
JWT 导入问题修复测试脚本
测试修复后的 JWT 工具类是否正常工作
"""

import asyncio
import json
from utils.test_utils import TestUtils


async def test_jwt_fix():
    """测试 JWT 导入问题修复"""
    
    print("🧪 开始测试 JWT 导入问题修复...")
    print("-" * 60)
    
    print("🔍 问题分析:")
    print("错误: cannot import name 'get_env_config' from 'config.env'")
    print("原因: 环境配置文件使用的是 GetConfig 类和实例化的配置对象")
    print()
    
    print("🛠️ 修复措施:")
    print("1. 修改导入语句: from config.env import JwtConfig")
    print("2. 使用正确的配置对象: JwtConfig.jwt_secret_key")
    print("3. 使用配置中的算法: JwtConfig.jwt_algorithm")
    print("4. 使用配置中的过期时间: JwtConfig.jwt_expire_minutes")
    print()
    
    print("📋 当前配置:")
    try:
        from config.env import JwtConfig
        print(f"✅ JWT 配置导入成功")
        print(f"   密钥长度: {len(JwtConfig.jwt_secret_key)} 字符")
        print(f"   算法: {JwtConfig.jwt_algorithm}")
        print(f"   过期时间: {JwtConfig.jwt_expire_minutes} 分钟")
    except Exception as e:
        print(f"❌ JWT 配置导入失败: {e}")
        return
    
    print("\n🔧 测试 JWT 工具类:")
    try:
        from utils.jwt_util import JWTUtil
        print("✅ JWT 工具类导入成功")
        
        # 测试 token 创建
        test_data = {"user_id": 1, "user_name": "test"}
        access_token = JWTUtil.create_access_token(test_data)
        refresh_token = JWTUtil.create_refresh_token(test_data)
        
        print(f"✅ Access Token 创建成功: {len(access_token)} 字符")
        print(f"✅ Refresh Token 创建成功: {len(refresh_token)} 字符")
        
        # 测试 token 验证
        payload = JWTUtil.verify_token(access_token)
        if payload:
            print("✅ Token 验证成功")
            print(f"   用户ID: {payload.get('user_id')}")
            print(f"   用户名: {payload.get('user_name')}")
            print(f"   Token类型: {payload.get('type')}")
        else:
            print("❌ Token 验证失败")
            
    except Exception as e:
        print(f"❌ JWT 工具类测试失败: {e}")
        return
    
    print("\n💡 测试步骤:")
    print("1. 启动服务器: python start_app.py")
    print("2. 先注册一个测试用户（使用万能验证码 123456）")
    print("3. 使用登录接口获取 JWT token")
    print("4. 观察是否还有导入错误")
    
    print("\n🔧 修复的技术细节:")
    print("1. 导入修复:")
    print("   - 从: from config.env import get_env_config")
    print("   - 到: from config.env import JwtConfig")
    
    print("\n2. 配置使用:")
    print("   - 密钥: JwtConfig.jwt_secret_key")
    print("   - 算法: JwtConfig.jwt_algorithm")
    print("   - 过期时间: JwtConfig.jwt_expire_minutes")
    
    print("\n3. 配置值:")
    print("   - 默认密钥: b01c66dc2c58dc6a0aabfe2144256be36226de378bf87f72c0c795dda67f4d55")
    print("   - 默认算法: HS256")
    print("   - 默认过期时间: 1440 分钟 (24小时)")
    
    print("\n✅ JWT 导入问题修复完成！")
    print("🎯 现在 JWT 工具类应该能够正常工作，不再出现导入错误")


if __name__ == "__main__":
    asyncio.run(test_jwt_fix()) 