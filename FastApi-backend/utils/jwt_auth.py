"""
JWT 认证中间件
用于验证和解析 JWT token
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from utils.jwt_util import JWTUtil


# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    获取当前用户信息
    
    Args:
        credentials: HTTP 认证凭据
        
    Returns:
        Dict: 用户信息
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    token = credentials.credentials
    
    # 验证 token
    payload = JWTUtil.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查 token 类型
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token类型",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """
    获取当前用户信息（可选认证）
    
    Args:
        credentials: HTTP 认证凭据（可选）
        
    Returns:
        Optional[Dict]: 用户信息，如果未提供token则返回None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def verify_token(token: str) -> Optional[Dict]:
    """
    验证 token（同步版本）
    
    Args:
        token: JWT token
        
    Returns:
        Optional[Dict]: 验证成功返回payload，失败返回None
    """
    return JWTUtil.verify_token(token)


def decode_token(token: str) -> Optional[Dict]:
    """
    解码 token（同步版本）
    
    Args:
        token: JWT token
        
    Returns:
        Optional[Dict]: 解码后的数据
    """
    return JWTUtil.decode_token(token) 