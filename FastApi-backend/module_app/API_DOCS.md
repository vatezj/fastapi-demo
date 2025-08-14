# APP 模块 API 文档

## 文档访问地址

### 1. 后台管理系统文档
- **Swagger UI**: `http://127.0.0.1:9099/admin/docs`
- **ReDoc**: `http://127.0.0.1:9099/admin/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9099/admin/openapi.json`

### 2. APP 模块文档
- **Swagger UI**: `http://127.0.0.1:9099/app/docs`
- **ReDoc**: `http://127.0.0.1:9099/app/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9099/app/openapi.json`

## 文档分离的优势

### 🎯 **清晰的角色分离**
- **后台管理文档**：面向系统管理员、运维人员
- **APP 接口文档**：面向移动端开发者、前端工程师

### 📱 **APP 模块专用功能**
- 移动端特有的接口说明
- 移动端认证流程
- 移动端数据格式
- 移动端错误码说明

### 🔧 **技术架构优势**
- 独立的 FastAPI 应用实例
- 独立的 OpenAPI 配置
- 独立的中间件和异常处理
- 便于独立部署和扩展

## API 接口路径结构

### 后台管理系统接口
```
/admin               - 后台管理模块根路径
├── /docs           - 后台管理文档
├── /redoc          - 后台管理 ReDoc
├── /openapi.json   - 后台管理 OpenAPI
├── /login          - 后台登录
├── /system/*       - 系统管理接口
├── /monitor/*      - 系统监控接口
└── /tool/*         - 工具接口
```

### APP 模块接口
```
/app                 - APP 模块根路径
├── /docs           - APP 接口文档
├── /redoc          - APP ReDoc
├── /openapi.json   - APP OpenAPI
├── /v1/auth/*      - APP 认证接口
├── /v1/user/*      - APP 用户接口
└── /v1/user/*      - APP 用户管理接口
```

## 使用说明

### 1. 后台管理系统开发
- 访问 `/admin/docs` 查看后台管理接口
- 使用后台管理相关的认证和权限
- 遵循后台管理的数据格式规范

### 2. APP 模块开发
- 访问 `/app/docs` 查看 APP 接口
- 使用 APP 模块的认证机制
- 遵循移动端的数据格式规范

### 3. 接口测试
- 后台接口：使用 `/docs` 中的 Swagger UI 测试
- APP 接口：使用 `/app/docs` 中的 Swagger UI 测试

## 配置说明

### 后台管理系统配置
```python
admin_app = FastAPI(
    title=f'{AppConfig.app_name} - 后台管理系统',
    description=f'{AppConfig.app_name}后台管理系统接口文档 - 面向系统管理员',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)
```

### APP 模块配置
```python
app_app = FastAPI(
    title=f'{AppConfig.app_name} - APP接口',
    description=f'{AppConfig.app_name}移动端APP接口文档 - 面向移动端开发者',
    docs_url='/app/docs',
    redoc_url='/app/redoc',
    openapi_url='/app/openapi.json',
)
```

## 注意事项

1. **路径前缀**：APP 模块的所有接口都以 `/app` 开头
2. **文档独立**：两个文档系统完全独立，互不影响
3. **认证分离**：后台管理和 APP 模块使用不同的认证机制
4. **数据格式**：两个系统可能使用不同的数据格式和验证规则

## 扩展建议

1. **独立部署**：可以将 APP 模块独立部署到不同的服务器
2. **负载均衡**：可以为 APP 模块配置专门的负载均衡策略
3. **监控分离**：可以为两个系统配置不同的监控和日志策略
4. **版本管理**：APP 模块可以独立进行版本管理和升级
