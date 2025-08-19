"""
游赚模块认证中间件
集成module_app的用户认证系统
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from config.get_redis import RedisUtil
from config.env import JwtConfig
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional
from module_app.dao.app_user_dao import AppUserDao
from module_app.entity.do.app_user_do import AppUser

# 创建HTTPBearer实例
security = HTTPBearer()

class YozuanAuthMiddleware:
    """游赚模块认证中间件"""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
    ) -> AppUser:
        """
        获取当前认证用户
        
        Args:
            credentials: HTTP认证凭据
            db: 数据库会话
            
        Returns:
            AppUser: 当前用户对象
            
        Raises:
            HTTPException: 认证失败时抛出
        """
        try:
            # 1. 获取token
            token = credentials.credentials
            
            # 2. 验证JWT token
            try:
                payload = jwt.decode(
                    token, 
                    JwtConfig.jwt_secret_key, 
                    algorithms=[JwtConfig.jwt_algorithm]
                )
                user_id = payload.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="无效的token格式"
                    )
            except InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token已失效，请重新登录"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token验证失败"
                )
            
            # 3. 从数据库获取用户信息
            user = await AppUserDao.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )
            
            # 4. 检查用户状态
            if user.status != "0":  # 0表示正常状态
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用户已被禁用"
                )
            
            # 5. Redis token验证（可选）
            try:
                redis = RedisUtil.get_redis()
                if redis:
                    redis_token = await redis.get(f"access_token:{user_id}")
                    if redis_token and token != redis_token:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="token已失效，请重新登录"
                        )
            except Exception:
                # Redis不可用时跳过验证
                pass
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证服务异常"
            )
    
    @staticmethod
    async def get_current_user_id(
        current_user: AppUser
    ) -> int:
        """
        获取当前用户ID
        
        Args:
            current_user: 当前用户对象
            
        Returns:
            int: 用户ID
        """
        return current_user.user_id
    
    @staticmethod
    async def get_current_user_info(
        current_user: AppUser
    ) -> dict:
        """
        获取当前用户信息
        
        Args:
            current_user: 当前用户对象
            
        Returns:
            dict: 用户信息
        """
        return {
            "user_id": current_user.user_id,
            "user_name": current_user.user_name,
            "nick_name": current_user.nick_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "sex": current_user.sex,
            "avatar": current_user.avatar,
            "status": current_user.status
        }


# 创建依赖函数
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AppUser:
    """获取当前认证用户依赖"""
    return await YozuanAuthMiddleware.get_current_user(credentials, db)


async def get_current_user_id(
    current_user: AppUser = Depends(get_current_user)
) -> int:
    """获取当前用户ID依赖"""
    return current_user.user_id


async def get_current_user_info(
    current_user: AppUser = Depends(get_current_user)
) -> dict:
    """获取当前用户信息依赖"""
    return {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "nick_name": current_user.nick_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "sex": current_user.sex,
        "avatar": current_user.avatar,
        "status": current_user.status
    }
