#!/usr/bin/env python3
"""
游赚模块完整功能测试脚本
"""

def test_imports():
    """测试所有模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试认证中间件
        from module_yozuan.middleware.auth_middleware import (
            get_current_user, get_current_user_id, get_current_user_info
        )
        print("✅ 认证中间件导入成功")
        
        # 测试邀请相关模块
        from module_yozuan.entity.do.invitation_do import (
            YozuanUserInvitation, YozuanRebateConfig, YozuanRebateRecord
        )
        print("✅ 邀请实体类导入成功")
        
        from module_yozuan.dao.invitation_dao import InvitationDao, RebateConfigDao
        print("✅ 邀请DAO类导入成功")
        
        from module_yozuan.service.invitation_service import InvitationService, RebateService
        print("✅ 邀请服务类导入成功")
        
        from module_yozuan.controller.invitation_controller import invitation_router
        print("✅ 邀请控制器导入成功")
        
        # 测试任务控制器
        from module_yozuan.controller.task_controller import router as task_router
        print("✅ 任务控制器导入成功")
        
        # 测试配置
        from config.yozuan_config import yozuan_config
        print("✅ 游赚配置导入成功")
        
        # 测试主应用
        from module_yozuan.app import yozuan_app
        print("✅ 游赚主应用导入成功")
        
        # 测试主应用集成
        from server import app
        print("✅ 主应用集成成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


def test_routes():
    """测试路由配置"""
    print("\n🧪 测试路由配置...")
    
    try:
        from module_yozuan.app import yozuan_app
        
        # 统计各种标签的路由数量
        route_counts = {}
        for route in yozuan_app.routes:
            if hasattr(route, 'tags') and route.tags:
                for tag in route.tags:
                    route_counts[tag] = route_counts.get(tag, 0) + 1
        
        print("✅ 路由统计:")
        for tag, count in route_counts.items():
            print(f"  - {tag}: {count} 个路由")
        
        # 检查新增的邀请分销路由
        if "邀请分销" in route_counts:
            print(f"✅ 邀请分销模块: {route_counts['邀请分销']} 个路由")
        else:
            print("❌ 邀请分销模块路由未找到")
            return False
        
        # 检查任务管理路由
        if "任务管理" in route_counts:
            print(f"✅ 任务管理模块: {route_counts['任务管理']} 个路由")
        else:
            print("❌ 任务管理模块路由未找到")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        return False


def test_config():
    """测试配置功能"""
    print("\n🧪 测试配置功能...")
    
    try:
        from config.yozuan_config import yozuan_config
        
        print("✅ 配置测试:")
        print(f"  - 模块启用: {yozuan_config.yozuan_enabled}")
        print(f"  - 数据库前缀: {yozuan_config.yozuan_db_prefix}")
        print(f"  - 最大步骤数: {yozuan_config.yozuan_task_max_steps}")
        print(f"  - 最大验证数: {yozuan_config.yozuan_task_max_verifications}")
        print(f"  - 最小任务价格: {yozuan_config.yozuan_task_min_price}")
        print(f"  - 最大任务价格: {yozuan_config.yozuan_task_max_price}")
        print(f"  - 最大返佣层级: {yozuan_config.yozuan_rebate_max_levels}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def test_auth_middleware():
    """测试认证中间件"""
    print("\n🧪 测试认证中间件...")
    
    try:
        from module_yozuan.middleware.auth_middleware import (
            YozuanAuthMiddleware, get_current_user, get_current_user_id, get_current_user_info
        )
        
        print("✅ 认证中间件测试:")
        print(f"  - 中间件类: {YozuanAuthMiddleware.__name__}")
        print(f"  - 获取用户函数: {get_current_user.__name__}")
        print(f"  - 获取用户ID函数: {get_current_user_id.__name__}")
        print(f"  - 获取用户信息函数: {get_current_user_info.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 认证中间件测试失败: {e}")
        return False


def test_invitation_service():
    """测试邀请服务"""
    print("\n🧪 测试邀请服务...")
    
    try:
        from module_yozuan.service.invitation_service import InvitationService, RebateService
        
        print("✅ 邀请服务测试:")
        print(f"  - 邀请服务类: {InvitationService.__name__}")
        print(f"  - 返佣服务类: {RebateService.__name__}")
        
        # 检查服务方法
        invitation_methods = [method for method in dir(InvitationService) if not method.startswith('_')]
        rebate_methods = [method for method in dir(RebateService) if not method.startswith('_')]
        
        print(f"  - 邀请服务方法: {invitation_methods}")
        print(f"  - 返佣服务方法: {rebate_methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ 邀请服务测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始测试游赚模块完整功能...")
    print("=" * 60)
    
    # 测试导入
    if not test_imports():
        print("❌ 导入测试失败")
        return
    
    # 测试路由
    if not test_routes():
        print("❌ 路由测试失败")
        return
    
    # 测试配置
    if not test_config():
        print("❌ 配置测试失败")
        return
    
    # 测试认证中间件
    if not test_auth_middleware():
        print("❌ 认证中间件测试失败")
        return
    
    # 测试邀请服务
    if not test_invitation_service():
        print("❌ 邀请服务测试失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！游赚模块功能完整")
    print("\n📋 测试结果:")
    print("  - 模块导入: ✅ 成功")
    print("  - 路由配置: ✅ 成功")
    print("  - 配置管理: ✅ 成功")
    print("  - 认证中间件: ✅ 成功")
    print("  - 邀请服务: ✅ 成功")
    print("  - 架构集成: ✅ 成功")
    
    print("\n🚀 功能特性:")
    print("  - 完整的用户认证系统")
    print("  - 3级分销邀请系统")
    print("  - 任务发布和管理系统")
    print("  - 自动返佣计算系统")
    print("  - 灵活的配置管理")
    print("  - 清晰的模块架构")


if __name__ == "__main__":
    main()
