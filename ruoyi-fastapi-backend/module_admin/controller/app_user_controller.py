from fastapi import APIRouter, Depends, Query, Body
from typing import List
# 后台管理模块直接使用shared模块的DAO，不需要服务层
from shared.entity.vo.app_user_vo import (
    AppAddUserModel, AppEditUserModel, AppUserQueryModel, AppUserPageQueryModel,
    AppResetPasswordModel, AppLoginModel, AppRegisterModel, AppSmsCodeModel,
    AppUserStatusModel, AppDeleteUserModel, AppLoginLogQueryModel, AppLoginLogPageQueryModel
)
from utils.response_util import ResponseUtil

# 创建APP用户管理路由
app_user_admin_router = APIRouter(prefix="/app-user", tags=["APP用户管理"])


# ==================== 用户管理接口 ====================

@app_user_admin_router.get("/list")
async def get_app_user_list(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name: str = Query(None, description="用户账号"),
    nick_name: str = Query(None, description="用户昵称"),
    email: str = Query(None, description="用户邮箱"),
    phone: str = Query(None, description="手机号码"),
    sex: str = Query(None, description="用户性别"),
    status: str = Query(None, description="帐号状态"),
    begin_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间")
):
    """获取APP用户列表（分页）"""
    from datetime import datetime
    
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
    
    return await AppUserService.get_user_list(query)


@app_user_admin_router.get("/{user_id}")
async def get_app_user_detail(user_id: int):
    """获取APP用户详情"""
    return await AppUserService.get_user_detail(user_id)


@app_user_admin_router.post("/add")
async def add_app_user(user_data: AppAddUserModel):
    """新增APP用户"""
    return await AppUserService.create_user(user_data)


@app_user_admin_router.put("/edit")
async def edit_app_user(user_data: AppEditUserModel):
    """编辑APP用户"""
    return await AppUserService.update_user(user_data)


@app_user_admin_router.delete("/delete")
async def delete_app_user(user_ids: List[int] = Body(..., description="用户ID列表")):
    """删除APP用户"""
    return await AppUserService.delete_user(user_ids)


@app_user_admin_router.put("/status")
async def change_app_user_status(user_data: AppUserStatusModel):
    """修改APP用户状态"""
    return await AppUserService.change_user_status(user_data)


@app_user_admin_router.put("/reset-password")
async def reset_app_user_password(password_data: AppResetPasswordModel):
    """重置APP用户密码"""
    return await AppUserService.reset_user_password(password_data)


# 后台管理模块不需要用户认证接口，这些接口只在APP模块中提供


# ==================== 登录日志接口 ====================

@app_user_admin_router.get("/login-log/list")
async def get_app_login_log_list(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name: str = Query(None, description="用户账号"),
    ipaddr: str = Query(None, description="登录IP地址"),
    status: str = Query(None, description="登录状态"),
    begin_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间")
):
    """获取APP登录日志列表（分页）"""
    from datetime import datetime
    
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
    
    return await AppLoginLogService.get_login_log_list(query)


@app_user_admin_router.delete("/login-log/delete")
async def delete_app_login_logs(log_ids: List[int] = Body(..., description="日志ID列表")):
    """删除APP登录日志"""
    return await AppLoginLogService.delete_login_logs(log_ids)


@app_user_admin_router.delete("/login-log/clean")
async def clean_app_login_logs(days: int = Query(30, description="清理天数")):
    """清理APP登录日志"""
    return await AppLoginLogService.clean_login_logs(days)
