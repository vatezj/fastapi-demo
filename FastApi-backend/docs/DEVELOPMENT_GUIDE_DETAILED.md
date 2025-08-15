# FastAPI 后端详细开发指南

## 1. 开发环境搭建

### 1.1 环境要求

#### 1.1.1 Python 环境
- **Python 版本**: 3.8+
- **推荐版本**: Python 3.9 或 3.10
- **虚拟环境**: 建议使用 venv 或 conda

#### 1.1.2 数据库环境
- **PostgreSQL**: 12+ (推荐)
- **MySQL**: 8.0+ (支持)
- **Redis**: 6.0+

#### 1.1.3 开发工具
- **IDE**: PyCharm, VS Code, Vim
- **代码检查**: flake8, black, isort
- **测试框架**: pytest, pytest-asyncio

### 1.2 环境配置

#### 1.2.1 创建虚拟环境
```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows

# 使用 conda
conda create -n fastapi-admin python=3.9
conda activate fastapi-admin
```

#### 1.2.2 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装代码检查工具
pip install flake8 black isort mypy
```

#### 1.2.3 环境变量配置
```bash
# 复制环境配置文件
cp config/env.py.example config/env.py

# 编辑配置文件
vim config/env.py
```

## 2. 项目结构详解

### 2.1 目录结构说明

```
FastApi-backend/
├── app.py                          # 应用入口文件
├── server.py                       # 服务器配置文件
├── start_app.py                    # 启动脚本
├── config/                         # 配置目录
│   ├── __init__.py
│   ├── env.py                      # 环境配置
│   ├── database.py                 # 数据库配置
│   ├── constant.py                 # 常量定义
│   ├── enums.py                    # 枚举定义
│   ├── get_db.py                   # 数据库连接管理
│   ├── get_redis.py                # Redis连接管理
│   └── get_scheduler.py            # 调度器管理
├── module_admin/                   # 系统管理模块
│   ├── __init__.py
│   ├── app.py                      # 模块应用
│   ├── controller/                 # 控制器层
│   ├── service/                    # 服务层
│   ├── dao/                        # 数据访问层
│   ├── entity/                     # 实体层
│   │   ├── do/                     # 数据对象
│   │   └── vo/                     # 视图对象
│   ├── aspect/                     # 切面编程
│   └── annotation/                 # 注解定义
├── module_app/                     # APP应用模块
├── module_generator/               # 代码生成模块
├── shared/                         # 共享模块
├── utils/                          # 工具模块
├── middlewares/                    # 中间件
├── exceptions/                     # 异常处理
├── logs/                          # 日志文件
├── tests/                         # 测试文件
└── docs/                          # 文档目录
```

### 2.2 核心文件说明

#### 2.2.1 配置文件 (config/)
- **env.py**: 环境变量和配置管理
- **database.py**: 数据库连接配置
- **constant.py**: 系统常量定义
- **enums.py**: 枚举类型定义

#### 2.2.2 模块文件 (module_*/)
- **app.py**: 模块应用配置
- **controller/**: HTTP请求处理
- **service/**: 业务逻辑处理
- **dao/**: 数据访问对象
- **entity/**: 数据模型定义

## 3. 开发规范

### 3.1 代码风格规范

#### 3.1.1 Python 代码规范
- **PEP 8**: 遵循 Python 官方代码规范
- **类型注解**: 使用类型提示 (Type Hints)
- **文档字符串**: 使用 docstring 格式
- **命名规范**: 使用 snake_case 命名

#### 3.1.2 代码示例
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

class UserService:
    """用户服务类
    
    提供用户相关的业务逻辑处理
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典，如果不存在返回None
            
        Raises:
            HTTPException: 当用户ID无效时抛出
        """
        if user_id <= 0:
            raise HTTPException(status_code=400, detail="无效的用户ID")
        
        # 业务逻辑实现
        return {"id": user_id, "name": "测试用户"}
```

### 3.2 项目结构规范

#### 3.2.1 模块命名规范
- **模块名**: 使用小写字母和下划线 (module_admin)
- **类名**: 使用大驼峰命名法 (UserService)
- **函数名**: 使用小写字母和下划线 (get_user_by_id)
- **变量名**: 使用小写字母和下划线 (user_list)

#### 3.2.2 文件命名规范
- **Python文件**: 使用小写字母和下划线 (user_service.py)
- **测试文件**: 以 test_ 开头 (test_user_service.py)
- **配置文件**: 使用描述性名称 (database_config.py)

## 4. 分层架构开发

### 4.1 Controller 层开发

#### 4.1.1 控制器职责
- 接收HTTP请求
- 参数验证和转换
- 调用Service层处理业务逻辑
- 返回HTTP响应

#### 4.1.2 控制器示例
```python
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config.get_db import get_db
from module_admin.service.user_service import UserService
from module_admin.entity.vo.user_vo import UserCreateModel, UserUpdateModel
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel

userController = APIRouter(prefix="/user", tags=["用户管理"])

@userController.get("/list", dependencies=[Depends(CheckUserInterfaceAuth('system:user:list'))])
async def get_user_list(
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页大小"),
    user_name: str = Query(None, description="用户名"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    try:
        user_service = UserService(db)
        result = await user_service.get_user_list(
            page_num=page_num,
            page_size=page_size,
            user_name=user_name
        )
        return ResponseUtil.success(data=result)
    except Exception as e:
        return ResponseUtil.error(msg=f"获取用户列表失败: {str(e)}")
```

## 5. 总结

本开发指南详细介绍了FastAPI后端的开发规范和实践，包括环境搭建、项目结构、开发规范和分层架构开发等核心内容。
