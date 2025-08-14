from fastapi import APIRouter, Depends, Query, Body
from typing import List
from ..service.app_user_service import AppUserService, AppLoginLogService
from ..entity.vo.app_user_vo import (
    AppAddUserModel, AppEditUserModel, AppUserQueryModel, AppUserPageQueryModel,
    AppResetPasswordModel, AppUserStatusModel, AppDeleteUserModel, 
    AppLoginLogQueryModel, AppLoginLogPageQueryModel
)
from utils.response_util import ResponseUtil
from utils.log_util import logger
from utils.cache_decorator import (
    cache_user_list, cache_user_detail, cache_login_log_list, 
    cache_stats_overview, invalidate_user_cache, invalidate_login_log_cache
)
from utils.monitor_decorator import (
    monitor_user_operations, monitor_login_operations, monitor_stats_operations,
    track_user_metrics, track_login_metrics
)
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService

# 创建后台管理接口路由 - 专门为后台管理系统提供
admin_interface_router = APIRouter(prefix="/admin", tags=["APP后台管理接口"])


# ==================== 用户管理接口 ====================

@admin_interface_router.get("/user/list", dependencies=[Depends(CheckUserInterfaceAuth('app:user:list'))])
@cache_user_list(expire_time=300)  # 缓存5分钟
@monitor_user_operations("admin_get_app_user_list")
@track_user_metrics("user_list_query", tags={"source": "admin"})
async def admin_get_app_user_list(
    page_num: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
    user_name: str = Query(None, description="用户账号（支持模糊查询）"),
    nick_name: str = Query(None, description="用户昵称（支持模糊查询）"),
    email: str = Query(None, description="用户邮箱（支持模糊查询）"),
    phone: str = Query(None, description="手机号码（支持模糊查询）"),
    sex: str = Query(None, description="用户性别（0男 1女 2未知）"),
    status: str = Query(None, description="帐号状态（0正常 1停用）"),
    begin_time: str = Query(None, description="开始时间（格式：YYYY-MM-DD）"),
    end_time: str = Query(None, description="结束时间（格式：YYYY-MM-DD）"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    后台管理 - 获取APP用户列表（分页）
    
    ## 功能说明
    获取APP用户列表，支持分页查询和多条件筛选
    
    ## 权限要求
    - 权限标识：`app:user:list`
    - 需要用户登录状态
    
    ## 查询参数
    - `page_num`: 页码，从1开始
    - `page_size`: 每页数量，最大100
    - `user_name`: 用户账号，支持模糊查询
    - `nick_name`: 用户昵称，支持模糊查询
    - `email`: 用户邮箱，支持模糊查询
    - `phone`: 手机号码，支持模糊查询
    - `sex`: 用户性别，0=男，1=女，2=未知
    - `status`: 帐号状态，0=正常，1=停用
    - `begin_time`: 开始时间，格式YYYY-MM-DD
    - `end_time`: 结束时间，格式YYYY-MM-DD
    
    ## 返回结果
    - 成功：返回用户列表和分页信息
    - 失败：返回错误信息
    
    ## 使用示例
    ```
    GET /app/v1/admin/user/list?page_num=1&page_size=10&status=0
    ```
    """
    from datetime import datetime
    
    try:
        # 构建查询参数
        query = AppUserPageQueryModel(
            page_num=page_num,
            page_size=page_size,
            user_name=user_name,
            nick_name=nick_name,
            email=email,
            phone=phone,
            sex=sex,
            status=status,
            begin_time=datetime.fromisoformat(begin_time) if begin_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None
        )
        
        result = await AppUserService.get_user_list(query)
        logger.info(f'后台管理获取APP用户列表成功，查询参数: {query.model_dump()}')
        return ResponseUtil.success(data=result, msg="获取APP用户列表成功")
    except Exception as e:
        logger.error(f'后台管理获取APP用户列表失败: {e}')
        return ResponseUtil.error(msg=f"获取APP用户列表失败: {str(e)}")


@admin_interface_router.get("/user/{user_id}", dependencies=[Depends(CheckUserInterfaceAuth('app:user:query'))])
@cache_user_detail(expire_time=600)  # 缓存10分钟
async def admin_get_app_user_detail(
    user_id: int,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 获取APP用户详情"""
    try:
        result = await AppUserService.get_user_detail(user_id)
        logger.info(f'后台管理获取APP用户详情成功，用户ID: {user_id}')
        return ResponseUtil.success(data=result, msg="获取APP用户详情成功")
    except Exception as e:
        logger.error(f'后台管理获取APP用户详情失败，用户ID: {user_id}, 错误: {e}')
        return ResponseUtil.error(msg=f"获取APP用户详情失败: {str(e)}")


@admin_interface_router.post("/user/add", dependencies=[Depends(CheckUserInterfaceAuth('app:user:add'))])
@invalidate_user_cache()  # 新增用户后失效相关缓存
@monitor_user_operations("admin_add_app_user")
@track_user_metrics("user_add", tags={"source": "admin"})
async def admin_add_app_user(
    user_data: AppAddUserModel,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    后台管理 - 新增APP用户
    
    ## 功能说明
    创建新的APP用户，支持基础信息和详细信息的创建
    
    ## 权限要求
    - 权限标识：`app:user:add`
    - 需要用户登录状态
    
    ## 请求参数
    - `user_name`: 用户账号（必填，唯一）
    - `nick_name`: 用户昵称（必填）
    - `password`: 用户密码（必填）
    - `email`: 用户邮箱（可选）
    - `phone`: 手机号码（可选）
    - `sex`: 用户性别（可选，0=男，1=女，2=未知）
    - `avatar`: 用户头像（可选）
    - `status`: 帐号状态（可选，0=正常，1=停用）
    - `remark`: 备注信息（可选）
    
    ## 详细信息（可选）
    - `real_name`: 真实姓名
    - `id_card`: 身份证号
    - `birthday`: 出生日期
    - `address`: 居住地址
    - `education`: 学历
    - `occupation`: 职业
    - `income_level`: 收入水平
    - `marital_status`: 婚姻状况
    - `emergency_contact`: 紧急联系人
    - `emergency_phone`: 紧急联系电话
    
    ## 返回结果
    - 成功：返回用户ID和成功消息
    - 失败：返回错误信息
    
    ## 使用示例
    ```json
    POST /app/v1/admin/user/add
    {
        "user_name": "testuser",
        "nick_name": "测试用户",
        "password": "password123",
        "email": "test@example.com",
        "phone": "13800138000",
        "sex": "0"
    }
    ```
    """
    try:
        result = await AppUserService.create_user(user_data)
        logger.info(f'后台管理新增APP用户成功，用户数据: {user_data.model_dump()}')
        return ResponseUtil.success(data=result, msg="新增APP用户成功")
    except Exception as e:
        logger.error(f'后台管理新增APP用户失败: {e}')
        return ResponseUtil.error(msg=f"新增APP用户失败: {str(e)}")


@admin_interface_router.put("/user/edit", dependencies=[Depends(CheckUserInterfaceAuth('app:user:edit'))])
@invalidate_user_cache()  # 编辑用户后失效相关缓存
async def admin_edit_app_user(
    user_data: AppEditUserModel,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 编辑APP用户"""
    try:
        result = await AppUserService.update_user(user_data)
        logger.info(f'后台管理编辑APP用户成功，用户数据: {user_data.model_dump()}')
        return ResponseUtil.success(data=result, msg="编辑APP用户成功")
    except Exception as e:
        logger.error(f'后台管理编辑APP用户失败: {e}')
        return ResponseUtil.error(msg=f"编辑APP用户失败: {str(e)}")


@admin_interface_router.delete("/user/delete", dependencies=[Depends(CheckUserInterfaceAuth('app:user:remove'))])
@invalidate_user_cache()  # 删除用户后失效相关缓存
async def admin_delete_app_user(
    user_ids: List[int] = Body(..., description="用户ID列表"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 删除APP用户"""
    try:
        result = await AppUserService.delete_user(user_ids)
        logger.info(f'后台管理删除APP用户成功，用户ID列表: {user_ids}')
        return ResponseUtil.success(data=result, msg="删除APP用户成功")
    except Exception as e:
        logger.error(f'后台管理删除APP用户失败: {e}')
        return ResponseUtil.error(msg=f"删除APP用户失败: {str(e)}")


@admin_interface_router.put("/user/status", dependencies=[Depends(CheckUserInterfaceAuth('app:user:edit'))])
async def admin_change_app_user_status(
    user_data: AppUserStatusModel,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 修改APP用户状态"""
    try:
        result = await AppUserService.change_user_status(user_data)
        logger.info(f'后台管理修改APP用户状态成功，用户数据: {user_data.model_dump()}')
        return ResponseUtil.success(data=result, msg="修改APP用户状态成功")
    except Exception as e:
        logger.error(f'后台管理修改APP用户状态失败: {e}')
        return ResponseUtil.error(msg=f"修改APP用户状态失败: {str(e)}")


@admin_interface_router.put("/user/reset-password", dependencies=[Depends(CheckUserInterfaceAuth('app:user:edit'))])
async def admin_reset_app_user_password(
    password_data: AppResetPasswordModel,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 重置APP用户密码"""
    try:
        result = await AppUserService.reset_user_password(password_data)
        logger.info(f'后台管理重置APP用户密码成功，用户ID: {password_data.user_id}')
        return ResponseUtil.success(data=result, msg="重置APP用户密码成功")
    except Exception as e:
        logger.error(f'后台管理重置APP用户密码失败: {e}')
        return ResponseUtil.error(msg=f"重置APP用户密码失败: {str(e)}")


# ==================== 登录日志管理接口 ====================

@admin_interface_router.get("/login-log/list", dependencies=[Depends(CheckUserInterfaceAuth('app:loginlog:list'))])
@cache_login_log_list(expire_time=300)  # 缓存5分钟
async def admin_get_app_login_log_list(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name: str = Query(None, description="用户账号"),
    ipaddr: str = Query(None, description="登录地址"),
    status: str = Query(None, description="登录状态"),
    begin_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 获取APP登录日志列表（分页）"""
    from datetime import datetime
    
    try:
        # 构建查询参数
        query = AppLoginLogPageQueryModel(
            page_num=page_num,
            page_size=page_size,
            user_name=user_name,
            ipaddr=ipaddr,
            status=status,
            begin_time=datetime.fromisoformat(begin_time) if begin_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None
        )
        
        result = await AppLoginLogService.get_login_log_list(query)
        logger.info(f'后台管理获取APP登录日志列表成功，查询参数: {query.model_dump()}')
        return ResponseUtil.success(data=result, msg="获取APP登录日志列表成功")
    except Exception as e:
        logger.error(f'后台管理获取APP登录日志列表失败: {e}')
        return ResponseUtil.error(msg=f"获取APP登录日志列表失败: {str(e)}")


@admin_interface_router.delete("/login-log/clear", dependencies=[Depends(CheckUserInterfaceAuth('app:loginlog:remove'))])
async def admin_clear_app_login_log(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 清空APP登录日志"""
    try:
        result = await AppLoginLogService.clear_login_log()
        logger.info('后台管理清空APP登录日志成功')
        return ResponseUtil.success(data=result, msg="清空APP登录日志成功")
    except Exception as e:
        logger.error(f'后台管理清空APP登录日志失败: {e}')
        return ResponseUtil.error(msg=f"清空APP登录日志失败: {str(e)}")


# ==================== 统计信息接口 ====================

@admin_interface_router.get("/stats/overview", dependencies=[Depends(CheckUserInterfaceAuth('app:stats:query'))])
@cache_stats_overview(expire_time=60)  # 缓存1分钟
async def admin_get_app_stats_overview(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """后台管理 - 获取APP统计概览"""
    try:
        # 这里可以添加统计逻辑，比如用户总数、今日新增用户数等
        stats = {
            "total_users": 0,  # 总用户数
            "active_users": 0,  # 活跃用户数
            "today_new_users": 0,  # 今日新增用户
            "total_login_logs": 0,  # 总登录日志数
        }
        
        logger.info('后台管理获取APP统计概览成功')
        return ResponseUtil.success(data=stats, msg="获取APP统计概览成功")
    except Exception as e:
        logger.error(f'后台管理获取APP统计概览失败: {e}')
        return ResponseUtil.error(msg=f"获取APP统计概览失败: {str(e)}")
