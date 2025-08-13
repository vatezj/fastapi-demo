# -*- coding: utf-8 -*-
"""
APP认证控制器
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel, Field
from shared.service.user_service import UserBaseService
from shared.dao.user_dao import UserDAO
from config.get_db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from datetime import datetime, timedelta
import hashlib

router = APIRouter(prefix="/auth", tags=["认证管理"])

# JWT配置
SECRET_KEY = "your-secret-key-here-make-it-long-and-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 安全配置
security = HTTPBearer()

# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    device_id: Optional[str] = Field(None, description="设备ID")
    push_token: Optional[str] = Field(None, description="推送令牌")

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")

class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user_info: dict = Field(..., description="用户信息")

# 依赖注入
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserBaseService:
    """获取用户服务实例"""
    user_dao = UserDAO(db)
    return UserBaseService(user_dao)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserBaseService = Depends(get_user_service)
):
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return user

def hash_password(password: str) -> str:
    """哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    login_data: LoginRequest,
    request: Request,
    user_service: UserBaseService = Depends(get_user_service)
):
    """用户登录"""
    try:
        # 根据用户名或邮箱获取用户
        user = await user_service.get_by_username_or_email(login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码（这里应该使用安全的密码验证）
        hashed_password = hash_password(login_data.password)
        if hashed_password != user.password:  # 实际使用时应该比较哈希值
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if user.status != '0':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 更新登录信息
        client_ip = request.client.host
        await user_service.update_login_info(user.id, client_ip)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        # 准备用户信息
        user_info = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "status": user.status
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(
    register_data: RegisterRequest,
    request: Request,
    user_service: UserBaseService = Depends(get_user_service)
):
    """用户注册"""
    try:
        # 验证密码确认
        if register_data.password != register_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致"
            )
        
        # 验证密码强度
        if not user_service.validate_password(register_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码必须包含至少6个字符，且包含数字和字母"
            )
        
        # 验证手机号格式
        if register_data.phone and not user_service.validate_phone(register_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号格式不正确"
            )
        
        # 检查用户名是否已存在
        if await user_service.exists(username=register_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if await user_service.exists(email=register_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 检查手机号是否已存在
        if register_data.phone and await user_service.exists(phone=register_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
        
        # 创建用户
        from shared.entity.vo.user_vo import UserCreateVO
        
        user_create_data = UserCreateVO(
            username=register_data.username,
            email=register_data.email,
            password=hash_password(register_data.password),  # 哈希密码
            nickname=register_data.nickname,
            phone=register_data.phone
        )
        
        user = await user_service.create_user(user_create_data)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        # 准备用户信息
        user_info = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "status": user.status
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_token(
    current_user = Depends(get_current_user),
    user_service: UserBaseService = Depends(get_user_service)
):
    """刷新访问令牌"""
    try:
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(current_user.id), "username": current_user.username},
            expires_delta=access_token_expires
        )
        
        # 准备用户信息
        user_info = {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": current_user.nickname,
            "email": current_user.email,
            "avatar": current_user.avatar,
            "status": current_user.status
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )

@router.get("/profile", summary="获取当前用户信息")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "status": current_user.status,
        "create_time": current_user.create_time
    }

@router.post("/logout", summary="用户登出")
async def logout(current_user = Depends(get_current_user)):
    """用户登出"""
    # 这里可以实现令牌黑名单等逻辑
    return {"message": "登出成功"} 