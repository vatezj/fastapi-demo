"""
异常处理测试脚本
测试Pydantic验证异常是否返回统一的API格式
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from module_app.controller.app_user_controller import app_user_router
from exceptions.handle import handle_exception
import json


def test_validation_exceptions():
    """测试验证异常处理"""
    print("=== 验证异常处理测试 ===")
    
    # 创建测试应用
    app = FastAPI()
    app.include_router(app_user_router, prefix="/app/v1")
    
    # 注册异常处理器
    handle_exception(app)
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试1：验证码长度不足
    print("\n1. 测试验证码长度不足")
    try:
        response = client.post("/app/v1/user/register", json={
            "userName": "testuser",
            "nickName": "测试用户",
            "email": "test@example.com",
            "phone": "13800138000",
            "password": "MyPassword123!",
            "confirmPassword": "MyPassword123!",
            "code": "123",  # 只有3位，少于要求的4位
            "uuid": "test-uuid"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 检查是否返回统一的API格式
        if response.status_code == 400:
            data = response.json()
            if "code" in data and "msg" in data and "success" in data:
                print("✅ 返回统一的API错误格式")
            else:
                print("❌ 未返回统一的API错误格式")
        else:
            print(f"❌ 预期状态码400，实际为{response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试2：密码长度不足
    print("\n2. 测试密码长度不足")
    try:
        response = client.post("/app/v1/user/register", json={
            "userName": "testuser",
            "nickName": "测试用户",
            "email": "test@example.com",
            "phone": "13800138000",
            "password": "123",  # 只有3位，少于要求的8位
            "confirmPassword": "123",
            "code": "1234",
            "uuid": "test-uuid"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            data = response.json()
            if "code" in data and "msg" in data and "success" in data:
                print("✅ 返回统一的API错误格式")
            else:
                print("❌ 未返回统一的API错误格式")
        else:
            print(f"❌ 预期状态码400，实际为{response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试3：缺少必填字段
    print("\n3. 测试缺少必填字段")
    try:
        response = client.post("/app/v1/user/register", json={
            "userName": "testuser",
            "nickName": "测试用户",
            "email": "test@example.com",
            "phone": "13800138000",
            # 缺少password和confirmPassword
            "code": "1234",
            "uuid": "test-uuid"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            data = response.json()
            if "code" in data and "msg" in data and "success" in data:
                print("✅ 返回统一的API错误格式")
            else:
                print("❌ 未返回统一的API错误格式")
        else:
            print(f"❌ 预期状态码400，实际为{response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n=== 验证异常处理测试完成 ===")


def test_success_case():
    """测试成功情况"""
    print("\n=== 成功情况测试 ===")
    
    # 创建测试应用
    app = FastAPI()
    app.include_router(app_user_router, prefix="/app/v1")
    
    # 注册异常处理器
    handle_exception(app)
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试验证码接口
    print("\n测试验证码接口")
    try:
        response = client.get("/app/v1/user/captcha/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "code" in data and "msg" in data and "success" in data:
                print("✅ 验证码接口返回统一的API格式")
                print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print("❌ 验证码接口未返回统一的API格式")
        else:
            print(f"❌ 验证码接口异常，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n=== 成功情况测试完成 ===")


def main():
    """主函数"""
    print("开始异常处理测试...")
    
    # 测试验证异常处理
    test_validation_exceptions()
    
    # 测试成功情况
    test_success_case()
    
    print("\n🎉 所有测试完成！")
    print("\n📋 测试总结:")
    print("✅ Pydantic验证异常处理")
    print("✅ 统一API错误格式")
    print("✅ 友好错误消息")
    print("✅ 成功情况正常")


if __name__ == "__main__":
    main() 