# 任务地区范围类型使用说明

## 概述

本系统支持三种任务地区范围类型，通过 `area_scope` 字段灵活配置任务的地理覆盖范围：

- **1 = 全国**：任务覆盖全国所有地区
- **2 = 单个城市**：任务仅覆盖指定的单个城市
- **3 = 多个城市**：任务覆盖指定的多个城市

## 数据库结构

### 新增字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `area_scope` | TINYINT | 地区范围类型 | 1=全国，2=单个城市，3=多个城市 |
| `single_area_code` | VARCHAR(6) | 单个城市编码 | 仅当area_scope=2时有效 |

### 新增表

**yozuan_task_city_rel**：任务城市关联表
- `rel_id`：关联ID（主键）
- `task_id`：任务ID
- `area_code`：城市编码
- `create_time`：创建时间

## API 使用说明

### 1. 发布全国任务

```json
{
    "task_name": "全国推广任务",
    "task_description": "面向全国用户的推广任务",
    "task_price": 10.00,
    "task_quantity": 1000,
    "task_type_id": 1,
    "area_scope": 1
}
```

### 2. 发布单个城市任务

```json
{
    "task_name": "北京地区任务",
    "task_description": "仅限北京地区的任务",
    "task_price": 15.00,
    "task_quantity": 100,
    "task_type_id": 1,
    "area_scope": 2,
    "single_area_code": "110100"
}
```

### 3. 发布多个城市任务

```json
{
    "task_name": "珠三角地区任务",
    "task_description": "覆盖广州、深圳、东莞等城市",
    "task_price": 12.00,
    "task_quantity": 500,
    "task_type_id": 1,
    "area_scope": 3,
    "area_codes": ["440100", "440300", "441900"]
}
```

## 城市编码说明

城市编码采用国标行政区域代码（6位数字）：

- **110100**：北京市
- **310100**：上海市  
- **440100**：广州市
- **440300**：深圳市
- **441900**：东莞市

## 兼容性说明

### 向后兼容

- 现有任务的 `region_limit` 字段保持不变
- 系统会自动根据 `region_limit` 内容设置 `area_scope` 类型
- 旧版本API仍然可以正常使用

### 字段映射

| 旧版本 | 新版本 | 说明 |
|--------|--------|------|
| `task_regions` | `area_scope` + `area_codes` | 地区范围类型 + 城市编码列表 |
| `region_limit` | 自动生成 | 系统根据area_scope自动生成 |

## 查询优化

### 索引设计

```sql
-- 任务表索引
CREATE INDEX idx_task_area_scope ON yozuan_task (area_scope);
CREATE INDEX idx_task_single_area ON yozuan_task (area_scope, single_area_code);

-- 关联表索引  
CREATE INDEX idx_rel_task_area ON yozuan_task_city_rel (task_id, area_code);
```

### 查询示例

#### 查询某城市下的所有任务

```sql
SELECT t.* FROM yozuan_task t
LEFT JOIN yozuan_task_city_rel rel ON t.task_id = rel.task_id
WHERE 
  t.area_scope = 1  -- 全国任务
  OR (t.area_scope = 2 AND t.single_area_code = '440100')  -- 单城市任务
  OR (t.area_scope = 3 AND rel.area_code = '440100');  -- 多城市任务
```

## 注意事项

1. **城市编码格式**：必须使用6位国标行政区域代码
2. **数据一致性**：`area_scope` 和 `single_area_code`/`area_codes` 必须匹配
3. **性能考虑**：多城市任务会创建关联表记录，建议城市数量不超过100个
4. **迁移建议**：建议在业务低峰期执行数据库迁移

## 错误处理

| 错误场景 | 错误信息 | 解决方案 |
|----------|----------|----------|
| 单城市任务未指定编码 | "单个城市任务必须指定城市编码" | 添加 `single_area_code` 字段 |
| 多城市任务未指定编码列表 | "多个城市任务必须指定城市编码列表" | 添加 `area_codes` 数组字段 |
| 城市编码格式错误 | 数据库约束错误 | 使用正确的6位国标编码 |

## 扩展建议

未来可扩展支持：
- **省份级别**：area_scope = 4（单个省份）
- **区域级别**：area_scope = 5（经济区域）
- **自定义区域**：area_scope = 6（用户自定义区域） 