# -*- coding: utf-8 -*-
"""
APP用户控制器
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from shared.entity.vo.user_vo import UserBaseVO, UserUpdateVO, UserPasswordVO
from shared.service.user_service import UserBaseService
from shared.dao.user_dao import UserDAO
from config.get_db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/user", tags=["用户管理"])

# 依赖注入
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserBaseService:
    """获取用户服务实例"""
    user_dao = UserDAO(db)
    return UserBaseService(user_dao)

@router.get("/profile", response_model=UserBaseVO, summary="获取用户资料")
async def get_user_profile(
    current_user_id: int = Depends(lambda: 1),  # 这里应该从JWT token中获取
    user_service: UserBaseService = Depends(get_user_service)
):
    """获取当前用户资料"""
    try:
        user = await user_service.get_by_id(current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user_service.convert_to_vo(user, UserBaseVO)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )

@router.put("/profile", response_model=UserBaseVO, summary="更新用户资料")
async def update_user_profile(
    user_data: UserUpdateVO,
    current_user_id: int = Depends(lambda: 1),  # 这里应该从JWT token中获取
    user_service: UserBaseService = Depends(get_user_service)
):
    """更新当前用户资料"""
    try:
        updated_user = await user_service.update_user(
            current_user_id, 
            user_data, 
            update_by=str(current_user_id)
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user_service.convert_to_vo(updated_user, UserBaseVO)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )

@router.put("/password", summary="修改密码")
async def change_password(
    password_data: UserPasswordVO,
    current_user_id: int = Depends(lambda: 1),  # 这里应该从JWT token中获取
    user_service: UserBaseService = Depends(get_user_service)
):
    """修改用户密码"""
    try:
        # 验证密码
        password_data.validate_passwords()
        
        # 验证旧密码
        user = await user_service.get_by_id(current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 这里应该验证旧密码是否正确
        # if not verify_password(password_data.old_password, user.password):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="旧密码错误"
        #     )
        
        # 更新密码
        success = await user_service.update_password(current_user_id, password_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码更新失败"
            )
        
        return {"message": "密码修改成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )

@router.get("/search", response_model=List[UserBaseVO], summary="搜索用户")
async def search_users(
    keyword: str,
    page: int = 1,
    size: int = 20,
    user_service: UserBaseService = Depends(get_user_service)
):
    """搜索用户"""
    try:
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 20
        
        users, total = await user_service.search_users(keyword, page, size)
        return user_service.convert_to_vo_list(users, UserBaseVO)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索用户失败: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserBaseVO, summary="获取指定用户资料")
async def get_user_by_id(
    user_id: int,
    user_service: UserBaseService = Depends(get_user_service)
):
    """根据ID获取用户资料"""
    try:
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user_service.convert_to_vo(user, UserBaseVO)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        ) 