# -*- coding: utf-8 -*-
"""
APP用户控制器
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..service.app_user_service import AppUserService
from ..entity.vo.app_user_vo import (
    AppAddUserModel, AppEditUserModel, AppUserQueryModel, AppUserPageQueryModel,
    AppResetPasswordModel, AppLoginModel, AppRegisterModel, AppSmsCodeModel,
    AppUserStatusModel, AppDeleteUserModel, AppLoginLogQueryModel, AppLoginLogPageQueryModel
)

app_user_router = APIRouter(prefix="/user", tags=["APP用户管理"])

# ==================== 用户管理接口 ====================

@app_user_router.get("/list")
async def get_app_user_list(
    user_name: str = Query(None, description="用户账号"),
    email: str = Query(None, description="用户邮箱"),
    phone: str = Query(None, description="手机号码"),
    status: str = Query(None, description="用户状态"),
    sex: str = Query(None, description="用户性别"),
    db: AsyncSession = Depends(get_db)
):
    """获取APP用户列表"""
    query_model = AppUserQueryModel(
        user_name=user_name,
        email=email,
        phone=phone,
        status=status,
        sex=sex
    )
    return await AppUserService.get_user_list(query_model, db)


@app_user_router.get("/page")
async def get_app_user_page(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name: str = Query(None, description="用户账号"),
    email: str = Query(None, description="用户邮箱"),
    phone: str = Query(None, description="手机号码"),
    status: str = Query(None, description="用户状态"),
    sex: str = Query(None, description="用户性别"),
    db: AsyncSession = Depends(get_db)
):
    """分页获取APP用户列表"""
    page_query = AppUserPageQueryModel(
        page_num=page_num,
        page_size=page_size,
        user_name=user_name,
        email=email,
        phone=phone,
        status=status,
        sex=sex
    )
    return await AppUserService.get_user_page(page_query, db)


@app_user_router.get("/{user_id}")
async def get_app_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取APP用户详情"""
    return await AppUserService.get_user_detail(user_id, db)


@app_user_router.post("/add")
async def add_app_user(
    user_data: AppAddUserModel,
    db: AsyncSession = Depends(get_db)
):
    """新增APP用户"""
    return await AppUserService.create_user(user_data, db)


@app_user_router.put("/edit")
async def edit_app_user(
    user_data: AppEditUserModel,
    db: AsyncSession = Depends(get_db)
):
    """编辑APP用户"""
    return await AppUserService.update_user(user_data, db)


@app_user_router.delete("/delete")
async def delete_app_user(
    delete_model: AppDeleteUserModel,
    db: AsyncSession = Depends(get_db)
):
    """删除APP用户"""
    return await AppUserService.delete_user(delete_model, db)


@app_user_router.put("/status")
async def change_app_user_status(
    status_model: AppUserStatusModel,
    db: AsyncSession = Depends(get_db)
):
    """修改APP用户状态"""
    return await AppUserService.change_user_status(status_model, db)


@app_user_router.put("/reset-password")
async def reset_app_user_password(
    reset_model: AppResetPasswordModel,
    db: AsyncSession = Depends(get_db)
):
    """重置APP用户密码"""
    return await AppUserService.reset_password(reset_model, db)


# ==================== 用户认证接口 ====================

@app_user_router.post("/login")
async def app_user_login(
    login_data: AppLoginModel,
    request,
    db: AsyncSession = Depends(get_db)
):
    """APP用户登录"""
    return await AppUserService.app_login(login_data, request, db)


@app_user_router.post("/register")
async def app_user_register(
    register_data: AppRegisterModel,
    db: AsyncSession = Depends(get_db)
):
    """APP用户注册"""
    return await AppUserService.app_register(register_data, db)


@app_user_router.post("/send-sms")
async def send_sms_code(
    sms_data: AppSmsCodeModel,
    db: AsyncSession = Depends(get_db)
):
    """发送短信验证码"""
    return await AppUserService.send_sms_code(sms_data, db)


# ==================== 登录日志接口 ====================

@app_user_router.get("/login-log/list")
async def get_app_login_log_list(
    user_name: str = Query(None, description="用户账号"),
    status: str = Query(None, description="登录状态"),
    start_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_db)
):
    """获取APP登录日志列表"""
    from datetime import datetime
    
    # 构建查询参数
    query_model = AppLoginLogQueryModel(
        user_name=user_name,
        status=status,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None
    )
    
    return await AppUserService.get_login_logs(query_model, db)


@app_user_router.get("/login-log/page")
async def get_app_login_log_page(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_name: str = Query(None, description="用户账号"),
    status: str = Query(None, description="登录状态"),
    start_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_db)
):
    """分页获取APP登录日志"""
    from datetime import datetime
    
    # 构建查询参数
    page_query = AppLoginLogPageQueryModel(
        page_num=page_num,
        page_size=page_size,
        user_name=user_name,
        status=status,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None
    )
    
    return await AppUserService.get_login_logs_page(page_query, db)
