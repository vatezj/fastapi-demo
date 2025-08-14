# 模块化代码生成器使用指南

## 概述

本文档描述了如何使用模块化代码生成器来生成符合模块化架构的代码。模块化代码生成器扩展现有的代码生成功能，支持生成不同模块类型的代码。

## 功能特性

### 1. 支持的模块类型
- **admin**: 管理模块（系统管理相关功能）
- **app**: APP模块（移动应用相关功能）
- **business**: 业务模块（具体业务功能）

### 2. 支持的前端框架
- **vue3**: Vue 3 + Element Plus
- **vue2**: Vue 2 + Element UI
- **react**: React（计划支持）

### 3. 生成的代码类型
- 后端代码（Controller、Service、DAO、Entity）
- 前端页面（Vue组件）
- API接口文件
- 路由配置
- 状态管理配置

## API接口

### 1. 获取支持的模块类型
```http
GET /tool/gen/modules/supported
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "获取支持的模块类型成功",
  "data": {
    "module_types": {
      "admin": {
        "name": "管理模块",
        "package": "module_admin",
        "description": "系统管理相关功能"
      },
      "app": {
        "name": "APP模块",
        "package": "module_app", 
        "description": "移动应用相关功能"
      }
    },
    "frontend_frameworks": ["vue2", "vue3", "react"]
  }
}
```

### 2. 获取模块配置模板
```http
GET /tool/gen/modules/config/{module_type}
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "获取模块配置模板成功",
  "data": {
    "type": "app",
    "name": "",
    "frontend": "vue3",
    "template": "crud",
    "output_path": "modules/app",
    "description": "移动应用相关功能"
  }
}
```

### 3. 生成模块化代码
```http
POST /tool/gen/modules/generate
```

**请求参数：**
```json
{
  "table_name": "app_user",
  "module_config": {
    "type": "app",
    "name": "user",
    "frontend": "vue3",
    "template": "crud",
    "table_comment": "APP用户表"
  }
}
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "模块化代码生成成功",
  "data": {
    "success": true,
    "message": "模块化代码生成成功",
    "backend": {
      "success": true,
      "message": "后端模块代码生成成功: module_app.user",
      "package_name": "module_app",
      "module_name": "user"
    },
    "frontend": {
      "success": true,
      "message": "前端模块代码配置生成成功: user",
      "views_path": "src/views/app",
      "api_path": "src/api/app",
      "store_path": "src/store/modules/app"
    },
    "router": {
      "success": true,
      "message": "路由配置生成成功",
      "router_config": {...}
    },
    "store": {
      "success": true,
      "message": "状态管理配置生成成功",
      "store_config": {...}
    }
  }
}
```

## 使用步骤

### 1. 准备数据库表
确保要生成代码的数据库表已经存在，并且表结构完整。

### 2. 配置模块信息
根据业务需求选择合适的模块类型和前端框架。

### 3. 调用生成接口
使用POST接口生成模块化代码，传入表名和模块配置。

### 4. 检查生成结果
查看生成的代码文件，确保符合预期。

## 配置说明

### 1. 模块类型配置
在 `config/env.py` 中的 `ModuleGenSettings` 类可以配置：
- 支持的模块类型
- 前端模块路径配置
- 前端模板类型

### 2. 自定义模块类型
可以通过修改配置来添加新的模块类型：
```python
module_types = {
    'custom': {
        'name': '自定义模块',
        'package': 'module_custom',
        'description': '自定义功能模块',
        'template_path': 'templates/module_custom'
    }
}
```

### 3. 自定义前端路径
可以配置不同模块的前端文件路径：
```python
frontend_modules = {
    'custom': {
        'path': 'src/views/custom',
        'api_path': 'src/api/custom',
        'store_path': 'src/store/modules/custom'
    }
}
```

## 模板定制

### 1. 后端模板
后端模板位于 `templates/module_*` 目录下，支持：
- Controller模板
- Service模板
- DAO模板
- Entity模板

### 2. 前端模板
前端模板位于 `templates/frontend/*` 目录下，支持：
- Vue页面模板
- API接口模板
- 状态管理模板

### 3. 模板变量
模板中可以使用以下变量：
- `{{ table_name }}`: 表名
- `{{ moduleName }}`: 模块名
- `{{ businessName }}`: 业务名
- `{{ className }}`: 类名
- `{{ functionName }}`: 功能名

## 注意事项

1. **权限要求**: 使用模块化代码生成器需要相应的权限
2. **文件覆盖**: 生成代码时注意文件覆盖问题
3. **路径配置**: 确保生成路径配置正确
4. **模板兼容**: 确保模板与目标框架兼容

## 故障排除

### 1. 常见错误
- 模块类型不支持
- 前端框架不支持
- 权限不足
- 路径不存在

### 2. 解决方案
- 检查模块类型配置
- 验证前端框架支持
- 确认用户权限
- 创建必要目录

## 扩展开发

### 1. 添加新模块类型
1. 在配置中添加新模块类型
2. 创建对应的模板目录
3. 实现模块特定的生成逻辑

### 2. 添加新前端框架
1. 在配置中添加新框架
2. 创建对应的模板文件
3. 实现框架特定的代码生成

### 3. 自定义生成逻辑
可以通过继承 `ModuleGenService` 类来实现自定义的代码生成逻辑。
