"""
JWT 工具类
用于生成和验证 JWT token
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Union
from config.env import JwtConfig


class JWTUtil:
    """JWT 工具类"""
    
    # 从环境配置获取密钥和配置
    SECRET_KEY = JwtConfig.jwt_secret_key
    ALGORITHM = JwtConfig.jwt_algorithm
    
    # Token 过期时间配置
    ACCESS_TOKEN_EXPIRE_MINUTES = JwtConfig.jwt_expire_minutes  # 从配置获取
    REFRESH_TOKEN_EXPIRE_DAYS = 7     # 刷新 token 7天过期
    
    @classmethod
    def create_access_token(
        cls, 
        data: Dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问 token
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def create_refresh_token(
        cls, 
        data: Dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新 token
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict]:
        """
        验证 token
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict]: 解码后的数据，如果验证失败返回 None
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict]:
        """
        解码 token（不验证签名，仅用于调试）
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict]: 解码后的数据
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except Exception:
            return None
    
    @classmethod
    def get_token_expiration(cls, token: str) -> Optional[datetime]:
        """
        获取 token 过期时间
        
        Args:
            token: JWT token
            
        Returns:
            Optional[datetime]: 过期时间
        """
        payload = cls.decode_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
    
    @classmethod
    def is_token_expired(cls, token: str) -> bool:
        """
        检查 token 是否过期
        
        Args:
            token: JWT token
            
        Returns:
            bool: 是否过期
        """
        payload = cls.decode_token(token)
        if not payload or "exp" not in payload:
            return True
        
        exp_timestamp = payload["exp"]
        current_timestamp = time.time()
        return current_timestamp > exp_timestamp
    
    @classmethod
    def create_token_pair(cls, user_data: Dict) -> Dict[str, str]:
        """
        创建 token 对（访问 token + 刷新 token）
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict[str, str]: 包含 access_token 和 refresh_token 的字典
        """
        access_token = cls.create_access_token(data=user_data)
        refresh_token = cls.create_refresh_token(data=user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[str]:
        """
        使用刷新 token 生成新的访问 token
        
        Args:
            refresh_token: 刷新 token
            
        Returns:
            Optional[str]: 新的访问 token，如果刷新失败返回 None
        """
        payload = cls.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # 移除过期时间和类型信息，重新生成访问 token
        user_data = {k: v for k, v in payload.items() if k not in ["exp", "type"]}
        return cls.create_access_token(data=user_data) 