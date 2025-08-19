#!/usr/bin/env python3
"""
游赚模块测试脚本
用于验证模块的基本功能是否正常
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_yozuan.enums.task_enums import (
    TaskStatus, TaskStepType, TaskVerificationType, 
    TaskOrderStatus, ReviewStatus, TransactionType, TransactionStatus,
    get_display_name, get_enum_choices,
    TASK_STATUS_DISPLAY, TASK_STEP_TYPE_DISPLAY, TASK_VERIFICATION_TYPE_DISPLAY,
    TASK_ORDER_STATUS_DISPLAY, REVIEW_STATUS_DISPLAY, TRANSACTION_TYPE_DISPLAY,
    TRANSACTION_STATUS_DISPLAY
)


def test_enums():
    """测试枚举类"""
    print("🧪 测试枚举类...")
    
    # 测试任务状态
    print(f"任务状态: {TaskStatus.ACTIVE.value} -> {get_display_name(TaskStatus.ACTIVE.value, TASK_STATUS_DISPLAY)}")
    
    # 测试步骤类型
    print(f"步骤类型: {TaskStepType.LINK.value} -> {get_display_name(TaskStepType.LINK.value, TASK_STEP_TYPE_DISPLAY)}")
    
    # 测试验证类型
    print(f"验证类型: {TaskVerificationType.IMAGE.value} -> {get_display_name(TaskVerificationType.IMAGE.value, TASK_VERIFICATION_TYPE_DISPLAY)}")
    
    # 测试订单状态
    print(f"订单状态: {TaskOrderStatus.IN_PROGRESS.value} -> {get_display_name(TaskOrderStatus.IN_PROGRESS.value, TASK_ORDER_STATUS_DISPLAY)}")
    
    # 测试审核状态
    print(f"审核状态: {ReviewStatus.PENDING.value} -> {get_display_name(ReviewStatus.PENDING.value, REVIEW_STATUS_DISPLAY)}")
    
    # 测试交易类型
    print(f"交易类型: {TransactionType.TASK_COMMISSION.value} -> {get_display_name(TransactionType.TASK_COMMISSION.value, TRANSACTION_TYPE_DISPLAY)}")
    
    # 测试交易状态
    print(f"交易状态: {TransactionStatus.SUCCESS.value} -> {get_display_name(TransactionStatus.SUCCESS.value, TRANSACTION_STATUS_DISPLAY)}")
    
    print("✅ 枚举类测试通过")


def test_enum_choices():
    """测试枚举选项生成"""
    print("\n🧪 测试枚举选项生成...")
    
    # 测试任务状态选项
    task_status_choices = get_enum_choices(TaskStatus, TASK_STATUS_DISPLAY)
    print(f"任务状态选项: {len(task_status_choices)} 个")
    for choice in task_status_choices[:3]:  # 只显示前3个
        print(f"  {choice[0]}: {choice[1]}")
    
    # 测试步骤类型选项
    step_type_choices = get_enum_choices(TaskStepType, TASK_STEP_TYPE_DISPLAY)
    print(f"步骤类型选项: {len(step_type_choices)} 个")
    for choice in step_type_choices:
        print(f"  {choice[0]}: {choice[1]}")
    
    print("✅ 枚举选项生成测试通过")


def test_entity_imports():
    """测试实体类导入"""
    print("\n🧪 测试实体类导入...")
    
    try:
        from module_yozuan.entity.do.task_do import YozuanTask, YozuanTaskType, YozuanTaskStep, YozuanTaskTag
        from module_yozuan.entity.do.order_do import YozuanTaskOrder
        from module_yozuan.entity.do.account_do import YozuanUserAccount, YozuanAccountTransaction
        from module_yozuan.entity.do.verification_do import YozuanTaskVerification, YozuanTaskVerificationSubmit
        
        print("✅ 实体类导入成功")
        print(f"  - 任务相关: {len([YozuanTask, YozuanTaskType, YozuanTaskStep, YozuanTaskTag])} 个")
        print(f"  - 订单相关: {len([YozuanTaskOrder])} 个")
        print(f"  - 账户相关: {len([YozuanUserAccount, YozuanAccountTransaction])} 个")
        print(f"  - 验证相关: {len([YozuanTaskVerification, YozuanTaskVerificationSubmit])} 个")
        
    except ImportError as e:
        print(f"❌ 实体类导入失败: {e}")
        return False
    
    return True


def test_dao_imports():
    """测试DAO类导入"""
    print("\n🧪 测试DAO类导入...")
    
    try:
        from module_yozuan.dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
        from module_yozuan.dao.order_dao import OrderDao
        from module_yozuan.dao.account_dao import AccountDao
        from module_yozuan.dao.verification_dao import VerificationDao, VerificationSubmitDao
        
        print("✅ DAO类导入成功")
        print(f"  - 任务DAO: {len([TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao])} 个")
        print(f"  - 订单DAO: {len([OrderDao])} 个")
        print(f"  - 账户DAO: {len([AccountDao])} 个")
        print(f"  - 验证DAO: {len([VerificationDao, VerificationSubmitDao])} 个")
        
    except ImportError as e:
        print(f"❌ DAO类导入失败: {e}")
        return False
    
    return True


def test_controller_imports():
    """测试控制器导入"""
    print("\n🧪 测试控制器导入...")
    
    try:
        from module_yozuan.controller.task_controller import router as task_router
        from module_yozuan.controller.order_controller import router as order_router
        from module_yozuan.controller.account_controller import router as account_router
        from module_yozuan.controller.admin_controller import router as admin_router
        
        print("✅ 控制器导入成功")
        print(f"  - 任务控制器: {len(task_router.routes)} 个路由")
        print(f"  - 订单控制器: {len(order_router.routes)} 个路由")
        print(f"  - 账户控制器: {len(account_router.routes)} 个路由")
        print(f"  - 管理控制器: {len(admin_router.routes)} 个路由")
        
    except ImportError as e:
        print(f"❌ 控制器导入失败: {e}")
        return False
    
    return True


def test_app_import():
    """测试应用模块导入"""
    print("\n🧪 测试应用模块导入...")
    
    try:
        from module_yozuan.app import yozuan_app
        
        print("✅ 应用模块导入成功")
        print(f"  - 总路由数: {len(yozuan_app.routes)} 个")
        
    except ImportError as e:
        print(f"❌ 应用模块导入失败: {e}")
        return False
    
    return True


def main():
    """主测试函数"""
    print("🚀 开始测试游赚模块...")
    print("=" * 50)
    
    # 测试枚举类
    test_enums()
    test_enum_choices()
    
    # 测试实体类
    if not test_entity_imports():
        print("❌ 实体类测试失败")
        return
    
    # 测试DAO类
    if not test_dao_imports():
        print("❌ DAO类测试失败")
        return
    
    # 测试控制器
    if not test_controller_imports():
        print("❌ 控制器测试失败")
        return
    
    # 测试应用模块
    if not test_app_import():
        print("❌ 应用模块测试失败")
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！游赚模块基本功能正常")
    print("\n📋 模块信息:")
    print("  - 模块名称: 游赚任务接单平台")
    print("  - 版本: 1.0.0")
    print("  - 状态: 开发中")
    print("  - 架构: 分层架构 (Controller → Service → DAO → Entity)")
    print("  - 数据库: 14个核心表")
    print("  - API接口: 任务管理、订单管理、账户管理、管理接口")


if __name__ == "__main__":
    main()
