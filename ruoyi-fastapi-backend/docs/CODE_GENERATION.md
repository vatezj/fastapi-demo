# 代码生成器使用指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的代码生成器使用方法，包括配置、模板定制、代码生成等。

## 代码生成器架构

### 1. 核心组件

```
module_generator/
├── controller/          # 控制器生成器
├── service/            # 服务层生成器
├── dao/               # 数据访问层生成器
├── entity/            # 实体生成器
└── templates/         # 代码模板
    ├── python/        # Python代码模板
    ├── vue/           # Vue前端模板
    ├── sql/           # SQL脚本模板
    └── js/            # JavaScript API模板
```

### 2. 生成流程

```
数据库表 → 表结构分析 → 模板渲染 → 代码生成 → 文件输出
    ↓         ↓         ↓         ↓         ↓
  元数据    字段信息    变量替换    代码生成    文件保存
```

## 配置管理

### 1. 基础配置

```python
class GenSettings:
    """代码生成配置"""
    author = 'insistence'                    # 作者
    package_name = 'module_admin.system'     # 包名
    auto_remove_pre = False                 # 是否自动移除表前缀
    table_prefix = 'sys_'                   # 表前缀
    allow_overwrite = False                 # 是否允许覆盖
    GEN_PATH = 'vf_admin/gen_path'          # 生成路径
```

### 2. 环境配置

```python
# 在 config/env.py 中配置
class GenSettings:
    """代码生成配置"""
    author = os.getenv('GEN_AUTHOR', 'insistence')
    package_name = os.getenv('GEN_PACKAGE_NAME', 'module_admin.system')
    auto_remove_pre = os.getenv('GEN_AUTO_REMOVE_PRE', 'false').lower() == 'true'
    table_prefix = os.getenv('GEN_TABLE_PREFIX', 'sys_')
    allow_overwrite = os.getenv('GEN_ALLOW_OVERWRITE', 'false').lower() == 'true'
    GEN_PATH = os.getenv('GEN_PATH', 'vf_admin/gen_path')
```

## 模板开发

### 1. Jinja2 模板语法

```jinja2
{# 变量使用 #}
{{ table_name }}

{# 条件判断 #}
{% if table.has_comment %}
    # {{ table.comment }}
{% endif %}

{# 循环遍历 #}
{% for column in columns %}
    {{ column.name }}: {{ column.type }},
{% endfor %}

{# 宏定义 #}
{% macro render_field(column) %}
    {{ column.name }}: {{ column.type }}
{% endmacro %}
```

### 2. 模板变量

```python
# 主要模板变量
table_info = {
    "name": "sys_user",           # 表名
    "comment": "用户表",           # 表注释
    "primary_key": "id",          # 主键字段
    "columns": [...],             # 字段列表
    "entity_name": "User",        # 实体名称
    "package_name": "module_admin.system"  # 包名
}

column_info = {
    "name": "username",           # 字段名
    "type": "VARCHAR(50)",       # 字段类型
    "comment": "用户名",          # 字段注释
    "is_nullable": False,        # 是否可为空
    "is_primary": False,         # 是否为主键
    "default_value": None        # 默认值
}
```

## 代码生成

### 1. 基础代码生成

```python
from module_generator.service.gen_service import GenService

class CodeGenerator:
    """代码生成器"""
    
    def __init__(self):
        self.gen_service = GenService()
    
    async def generate_code(self, table_name: str):
        """生成完整代码"""
        try:
            # 1. 分析表结构
            table_info = await self.gen_service.analyze_table(table_name)
            
            # 2. 生成后端代码
            await self.generate_backend_code(table_info)
            
            # 3. 生成前端代码
            await self.generate_frontend_code(table_info)
            
            # 4. 生成数据库脚本
            await self.generate_sql_script(table_info)
            
            print(f"代码生成完成: {table_name}")
            
        except Exception as e:
            print(f"代码生成失败: {e}")
            raise
    
    async def generate_backend_code(self, table_info: dict):
        """生成后端代码"""
        # 生成DO实体
        await self.gen_service.generate_do(table_info)
        
        # 生成VO对象
        await self.gen_service.generate_vo(table_info)
        
        # 生成DAO层
        await self.gen_service.generate_dao(table_info)
        
        # 生成Service层
        await self.gen_service.generate_service(table_info)
        
        # 生成Controller层
        await self.gen_service.generate_controller(table_info)
    
    async def generate_frontend_code(self, table_info: dict):
        """生成前端代码"""
        # 生成Vue页面
        await self.gen_service.generate_vue_page(table_info)
        
        # 生成API接口
        await self.gen_service.generate_api_js(table_info)
    
    async def generate_sql_script(self, table_info: dict):
        """生成SQL脚本"""
        await self.gen_service.generate_sql(table_info)
```

### 2. 批量代码生成

```python
async def batch_generate_code(table_names: List[str]):
    """批量生成代码"""
    generator = CodeGenerator()
    
    for table_name in table_names:
        print(f"正在生成表 {table_name} 的代码...")
        await generator.generate_code(table_name)
    
    print("批量代码生成完成")

# 使用示例
tables = ["sys_user", "sys_role", "sys_menu", "sys_dept"]
await batch_generate_code(tables)
```

## 模板定制

### 1. Python 代码模板

#### Controller 模板
```jinja2
# {{ table.comment }}控制器
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from {{ package_name }}.entity.vo.{{ entity_name.lower() }}_vo import {{ entity_name }}VO, {{ entity_name }}AddVO, {{ entity_name }}UpdateVO
from {{ package_name }}.service.{{ entity_name.lower() }}_service import {{ entity_name }}Service
from utils.response_util import ResponseResult

router = APIRouter(prefix="/{{ entity_name.lower() }}", tags=["{{ table.comment }}"])

@router.get("/list", response_model=List[{{ entity_name }}VO])
async def get_{{ entity_name.lower() }}_list():
    """获取{{ table.comment }}列表"""
    service = {{ entity_name }}Service()
    return await service.get_list()

@router.get("/page", response_model=PageResult[{{ entity_name }}VO])
async def get_{{ entity_name.lower() }}_page(page_query: PageQuery = Depends()):
    """分页获取{{ table.comment }}列表"""
    service = {{ entity_name }}Service()
    return await service.get_page_list(page_query)

@router.get("/{id}", response_model={{ entity_name }}VO)
async def get_{{ entity_name.lower() }}_by_id(id: int):
    """根据ID获取{{ table.comment }}"""
    service = {{ entity_name }}Service()
    return await service.get_by_id(id)

@router.post("/", response_model=ResponseResult)
async def create_{{ entity_name.lower() }}(data: {{ entity_name }}AddVO):
    """创建{{ table.comment }}"""
    service = {{ entity_name }}Service()
    return await service.create(data)

@router.put("/{id}", response_model=ResponseResult)
async def update_{{ entity_name.lower() }}(id: int, data: {{ entity_name }}UpdateVO):
    """更新{{ table.comment }}"""
    service = {{ entity_name }}Service()
    return await service.update(id, data)

@router.delete("/{id}", response_model=ResponseResult)
async def delete_{{ entity_name.lower() }}(id: int):
    """删除{{ table.comment }}"""
    service = {{ entity_name }}Service()
    return await service.delete(id)
```

#### Service 模板
```jinja2
# {{ table.comment }}服务
from typing import List, Optional
from {{ package_name }}.entity.do.{{ entity_name.lower() }}_do import {{ entity_name }}DO
from {{ package_name }}.entity.vo.{{ entity_name.lower() }}_vo import {{ entity_name }}AddVO, {{ entity_name }}UpdateVO
from {{ package_name }}.dao.{{ entity_name.lower() }}_dao import {{ entity_name }}DAO
from utils.page_util import PageQuery, PageResult

class {{ entity_name }}Service:
    """{{ table.comment }}服务"""
    
    def __init__(self):
        self.dao = {{ entity_name }}DAO()
    
    async def get_list(self) -> List[{{ entity_name }}DO]:
        """获取{{ table.comment }}列表"""
        return await self.dao.get_all()
    
    async def get_page_list(self, page_query: PageQuery) -> PageResult[{{ entity_name }}DO]:
        """分页获取{{ table.comment }}列表"""
        return await self.dao.get_page_list(page_query)
    
    async def get_by_id(self, id: int) -> Optional[{{ entity_name }}DO]:
        """根据ID获取{{ table.comment }}"""
        return await self.dao.get_by_id(id)
    
    async def create(self, data: {{ entity_name }}AddVO) -> {{ entity_name }}DO:
        """创建{{ table.comment }}"""
        entity = {{ entity_name }}DO(**data.dict())
        return await self.dao.create(entity)
    
    async def update(self, id: int, data: {{ entity_name }}UpdateVO) -> Optional[{{ entity_name }}DO]:
        """更新{{ table.comment }}"""
        return await self.dao.update(id, data.dict(exclude_unset=True))
    
    async def delete(self, id: int) -> bool:
        """删除{{ table.comment }}"""
        return await self.dao.delete(id)
```

### 2. Vue 前端模板

#### 列表页面模板
```vue
<template>
  <div class="app-container">
    <!-- 搜索表单 -->
    <el-form :model="queryParams" ref="queryForm" :inline="true">
      {% for column in columns %}
      {% if column.is_searchable %}
      <el-form-item label="{{ column.comment }}" prop="{{ column.name }}">
        <el-input
          v-model="queryParams.{{ column.name }}"
          placeholder="请输入{{ column.comment }}"
          clearable
        />
      </el-form-item>
      {% endif %}
      {% endfor %}
      
      <el-form-item>
        <el-button type="primary" @click="handleQuery">搜索</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" @click="handleAdd">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="success" @click="handleUpdate">修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </el-col>
    </el-row>
    
    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="dataList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      {% for column in columns %}
      <el-table-column label="{{ column.comment }}" prop="{{ column.name }}" />
      {% endfor %}
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button type="text" @click="handleUpdate(scope.row)">修改</el-button>
          <el-button type="text" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页组件 -->
    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />
    
    <!-- 添加/修改对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        {% for column in columns %}
        {% if not column.is_primary %}
        <el-form-item label="{{ column.comment }}" prop="{{ column.name }}">
          <el-input v-model="form.{{ column.name }}" placeholder="请输入{{ column.comment }}" />
        </el-form-item>
        {% endif %}
        {% endfor %}
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { list{{ entity_name }}, get{{ entity_name }}, del{{ entity_name }}, add{{ entity_name }}, update{{ entity_name }} } from "@/api/{{ entity_name.lower() }}";

export default {
  name: "{{ entity_name }}",
  data() {
    return {
      // 遮罩层
      loading: true,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // {{ table.comment }}表格数据
      dataList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        {% for column in columns %}
        {% if column.is_searchable %}
        {{ column.name }}: null,
        {% endif %}
        {% endfor %}
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        {% for column in columns %}
        {% if column.is_required %}
        {{ column.name }}: [
          { required: true, message: "{{ column.comment }}不能为空", trigger: "blur" }
        ],
        {% endif %}
        {% endfor %}
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询{{ table.comment }}列表 */
    getList() {
      this.loading = true;
      list{{ entity_name }}(this.queryParams).then(response => {
        this.dataList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        {% for column in columns %}
        {% if not column.is_primary %}
        {{ column.name }}: null,
        {% endif %}
        {% endfor %}
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.id);
      this.single = selection.length !== 1;
      this.multiple = !selection.length;
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加{{ table.comment }}";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids[0];
      get{{ entity_name }}(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改{{ table.comment }}";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.id != null) {
            update{{ entity_name }}(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            add{{ entity_name }}(this.form).then(response => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const ids = row.id || this.ids;
      this.$modal.confirm('是否确认删除{{ table.comment }}编号为"' + ids + '"的数据项？').then(function() {
        return del{{ entity_name }}(ids);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    }
  }
};
</script>
```

### 3. SQL 脚本模板

```sql
-- {{ table.comment }}表
CREATE TABLE {{ table.name }} (
    {% for column in columns %}
    {{ column.name }} {{ column.type }}{% if column.length %}({{ column.length }}){% endif %}{% if column.is_nullable == false %} NOT NULL{% endif %}{% if column.default_value %} DEFAULT {{ column.default_value }}{% endif %}{% if column.comment %}{% if column.comment != '' %} COMMENT '{{ column.comment }}'{% endif %}{% endif %}{% if not loop.last %},{% endif %}
    {% endfor %}
    {% if table.primary_key %}
    PRIMARY KEY ({{ table.primary_key }})
    {% endif %}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{{ table.comment }}';

-- 添加索引
{% for column in columns %}
{% if column.is_index %}
{% if column.is_unique %}
ALTER TABLE {{ table.name }} ADD UNIQUE KEY uk_{{ column.name }} ({{ column.name }});
{% else %}
ALTER TABLE {{ table.name }} ADD KEY idx_{{ column.name }} ({{ column.name }});
{% endif %}
{% endif %}
{% endfor %}

-- 插入初始数据
{% if table.has_initial_data %}
INSERT INTO {{ table.name }} ({% for column in columns %}{{ column.name }}{% if not loop.last %}, {% endif %}{% endfor %}) VALUES
{% for row in table.initial_data %}
({{ row.values|join(', ') }}){% if not loop.last %},{% endif %}
{% endfor %};
{% endif %}
```

## 高级功能

### 1. 自定义模板

```python
class CustomTemplateGenerator:
    """自定义模板生成器"""
    
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_template(self, template_name: str, context: dict) -> str:
        """渲染模板"""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def generate_custom_code(self, table_info: dict, template_name: str, output_file: str):
        """生成自定义代码"""
        # 渲染模板
        code = self.render_template(template_name, table_info)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"自定义代码生成完成: {output_file}")

# 使用示例
custom_generator = CustomTemplateGenerator("custom_templates")
custom_generator.generate_custom_code(
    table_info,
    "custom_service.py.jinja2",
    f"output/custom_{table_info['entity_name'].lower()}_service.py"
)
```

### 2. 模板继承

```jinja2
{# base_template.py.jinja2 #}
class Base{{ entity_name }}Service:
    """基础{{ table.comment }}服务"""
    
    def __init__(self):
        self.dao = {{ entity_name }}DAO()
    
    async def get_by_id(self, id: int):
        """根据ID获取{{ table.comment }}"""
        return await self.dao.get_by_id(id)
    
    {% block custom_methods %}{% endblock %}

{# custom_service.py.jinja2 #}
{% extends "base_template.py.jinja2" %}

{% block custom_methods %}
    async def custom_method(self):
        """自定义方法"""
        pass
{% endblock %}
```

## 使用示例

### 1. 基本使用

```python
# 1. 创建代码生成器
generator = CodeGenerator()

# 2. 生成单个表的代码
await generator.generate_code("sys_user")

# 3. 批量生成代码
tables = ["sys_user", "sys_role", "sys_menu"]
for table in tables:
    await generator.generate_code(table)
```

### 2. 自定义配置

```python
# 自定义生成配置
custom_config = {
    "author": "your_name",
    "package_name": "your_package",
    "table_prefix": "your_",
    "output_path": "custom_output"
}

# 使用自定义配置生成代码
generator = CodeGenerator(custom_config)
await generator.generate_code("your_table")
```

### 3. 模板定制

```python
# 1. 创建自定义模板目录
custom_templates = "custom_templates/"
os.makedirs(custom_templates, exist_ok=True)

# 2. 复制并修改模板文件
shutil.copy("templates/python/controller.py.jinja2", 
            f"{custom_templates}/controller.py.jinja2")

# 3. 使用自定义模板生成代码
custom_generator = CustomTemplateGenerator(custom_templates)
custom_generator.generate_custom_code(table_info, "controller.py.jinja2", 
                                    "output/custom_controller.py")
```

## 最佳实践

### 1. 模板设计原则
- **模块化**: 将复杂模板拆分为多个小模板
- **可复用**: 设计通用的模板组件
- **易维护**: 使用清晰的变量命名和注释
- **灵活性**: 支持条件渲染和循环

### 2. 代码生成原则
- **一致性**: 生成的代码风格保持一致
- **完整性**: 生成完整的CRUD功能
- **可扩展**: 生成的代码易于扩展和修改
- **标准化**: 遵循项目编码规范

### 3. 性能优化
- **模板缓存**: 缓存编译后的模板
- **批量生成**: 支持批量生成提高效率
- **增量更新**: 只更新变更的文件
- **并行处理**: 支持并行生成多个文件

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 