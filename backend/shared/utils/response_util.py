# -*- coding: utf-8 -*-
"""
统一响应工具
"""

from typing import Any, Optional, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status

class ResponseResult(BaseModel):
    """统一响应结果"""
    
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: Optional[str] = None
    
    class Config:
        json_encoders = {
            # 可以添加自定义的JSON编码器
        }

class PageResult(BaseModel):
    """分页结果"""
    
    list: list
    pagination: dict
    
    class Config:
        json_encoders = {
            # 可以添加自定义的JSON编码器
        }

def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200
) -> ResponseResult:
    """成功响应"""
    from datetime import datetime
    
    return ResponseResult(
        code=code,
        message=message,
        data=data,
        timestamp=datetime.now().isoformat()
    )

def error_response(
    message: str = "error",
    code: int = 500,
    data: Any = None
) -> ResponseResult:
    """错误响应"""
    from datetime import datetime
    
    return ResponseResult(
        code=code,
        message=message,
        data=data,
        timestamp=datetime.now().isoformat()
    )

def page_response(
    items: list,
    page: int,
    size: int,
    total: int
) -> ResponseResult:
    """分页响应"""
    pagination = {
        "page": page,
        "size": size,
        "total": total,
        "pages": (total + size - 1) // size,
        "has_next": page * size < total,
        "has_prev": page > 1
    }
    
    page_result = PageResult(
        list=items,
        pagination=pagination
    )
    
    return success_response(data=page_result)

# 预定义的响应
def not_found_response(message: str = "资源不存在") -> ResponseResult:
    """404响应"""
    return error_response(message=message, code=404)

def unauthorized_response(message: str = "未授权访问") -> ResponseResult:
    """401响应"""
    return error_response(message=message, code=401)

def forbidden_response(message: str = "禁止访问") -> ResponseResult:
    """403响应"""
    return error_response(message=message, code=403)

def validation_error_response(message: str = "参数验证失败", errors: Any = None) -> ResponseResult:
    """400响应"""
    return error_response(message=message, code=400, data=errors)

def server_error_response(message: str = "服务器内部错误") -> ResponseResult:
    """500响应"""
    return error_response(message=message, code=500)

# 快速响应函数
def success(data: Any = None, message: str = "success") -> dict:
    """快速成功响应"""
    return success_response(data=data, message=message).dict()

def error(message: str = "error", code: int = 500) -> dict:
    """快速错误响应"""
    return error_response(message=message, code=code).dict()

def page(items: list, page: int, size: int, total: int) -> dict:
    """快速分页响应"""
    return page_response(items=items, page=page, size=size, total=total).dict() 