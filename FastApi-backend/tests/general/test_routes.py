"""
路由测试脚本
测试验证码路由是否正确配置
"""

from fastapi.testclient import TestClient
from fastapi import FastAPI
from module_app.controller.app_user_controller import app_user_router
import json


def test_routes():
    """测试路由配置"""
    print("=== 路由测试 ===")
    
    # 创建测试应用
    app = FastAPI()
    app.include_router(app_user_router, prefix="/app/v1")
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试验证码路由
    print("\n1. 测试验证码路由")
    try:
        response = client.get("/app/v1/user/captcha/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 验证码路由正常")
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 验证码路由异常: {response.text}")
    except Exception as e:
        print(f"❌ 验证码路由测试失败: {e}")
    
    # 测试用户详情路由
    print("\n2. 测试用户详情路由")
    try:
        response = client.get("/app/v1/user/123")
        print(f"状态码: {response.status_code}")
        if response.status_code == 422:  # 422 是正常的，因为缺少数据库依赖
            print("✅ 用户详情路由正常（422是预期的，因为缺少数据库依赖）")
        else:
            print(f"用户详情路由响应: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户详情路由测试失败: {e}")
    
    # 测试不存在的路由
    print("\n3. 测试不存在的路由")
    try:
        response = client.get("/app/v1/user/nonexistent")
        print(f"状态码: {response.status_code}")
        if response.status_code == 422:  # 422 是正常的，因为参数类型不匹配
            print("✅ 路由匹配正常（422是预期的，因为参数类型不匹配）")
        else:
            print(f"不存在的路由响应: {response.status_code}")
    except Exception as e:
        print(f"❌ 不存在的路由测试失败: {e}")
    
    print("\n=== 路由测试完成 ===")


def test_route_order():
    """测试路由顺序"""
    print("\n=== 路由顺序测试 ===")
    
    # 创建测试应用
    app = FastAPI()
    app.include_router(app_user_router, prefix="/app/v1")
    
    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods) if hasattr(route, 'methods') else []
            })
    
    # 过滤用户相关路由
    user_routes = [r for r in routes if '/user' in r['path']]
    
    print("用户模块路由列表:")
    for i, route in enumerate(user_routes):
        print(f"{i+1}. {route['path']} - {route['methods']}")
    
    # 检查验证码路由是否在用户ID路由之前
    captcha_index = None
    user_id_index = None
    
    for i, route in enumerate(user_routes):
        if route['path'] == '/app/v1/user/captcha/':
            captcha_index = i
        elif route['path'] == '/app/v1/user/{user_id}':
            user_id_index = i
    
    if captcha_index is not None and user_id_index is not None:
        if captcha_index < user_id_index:
            print("✅ 验证码路由在用户ID路由之前，顺序正确")
        else:
            print("❌ 验证码路由在用户ID路由之后，顺序错误")
    else:
        print("⚠️ 无法确定路由顺序")


if __name__ == "__main__":
    test_routes()
    test_route_order() 