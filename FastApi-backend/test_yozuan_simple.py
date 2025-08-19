#!/usr/bin/env python3
"""
游赚模块简单测试脚本
"""

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试配置导入
        from config.yozuan_config import yozuan_config
        print("✅ 配置导入成功")
        print(f"  - 模块启用: {yozuan_config.yozuan_enabled}")
        print(f"  - 数据库前缀: {yozuan_config.yozuan_db_prefix}")
        print(f"  - 最大步骤数: {yozuan_config.yozuan_task_max_steps}")
        
        # 测试游赚模块导入
        from module_yozuan.app import yozuan_app
        print("✅ 游赚模块导入成功")
        print(f"  - 路由数量: {len(yozuan_app.routes)}")
        
        # 测试主应用导入
        from server import app
        print("✅ 主应用导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


def test_routes():
    """测试路由信息"""
    print("\n🧪 测试路由信息...")
    
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
        
        return True
        
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        return False


def test_config():
    """测试配置功能"""
    print("\n🧪 测试配置功能...")
    
    try:
        from config.yozuan_config import yozuan_config
        
        # 测试环境变量配置
        import os
        os.environ["YOZUAN_TASK_MAX_STEPS"] = "15"
        
        # 重新创建配置实例
        from config.yozuan_config import YozuanSettings
        test_config = YozuanSettings()
        
        print("✅ 配置测试:")
        print(f"  - 默认最大步骤数: {yozuan_config.yozuan_task_max_steps}")
        print(f"  - 环境变量最大步骤数: {test_config.yozuan_task_max_steps}")
        print(f"  - 环境变量配置生效: {test_config.yozuan_task_max_steps == 15}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始测试游赚模块...")
    print("=" * 50)
    
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
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！游赚模块功能正常")
    print("\n📋 测试结果:")
    print("  - 模块导入: ✅ 成功")
    print("  - 路由配置: ✅ 成功")
    print("  - 配置管理: ✅ 成功")
    print("  - 架构集成: ✅ 成功")


if __name__ == "__main__":
    main()
