# 地区数据插入使用说明

## 概述

本程序用于将 `area-city.json` 文件中的地区数据插入到 `yozuan_task_region` 表中，为任务地区范围功能提供基础数据支持。

## 文件结构

```
module_yozuan/
├── scripts/
│   └── insert_region_data.py          # 地区数据插入脚本
├── sql/
│   └── create_region_table.sql        # 地区表建表SQL
├── service/
│   └── region_service.py              # 地区数据服务
├── controller/
│   └── region_data_controller.py      # 地区数据API控制器
└── docs/
    └── REGION_DATA_INSERT_README.md   # 本说明文档
```

## 使用方法

### 1. 准备数据文件

确保 `area-city.json` 文件位于 `module_yozuan/scripts/` 目录下。

### 2. 执行数据插入

```bash
# 进入项目根目录
cd /path/to/FastApi-backend

# 执行插入脚本
uv run python module_yozuan/scripts/insert_region_data.py
```

### 3. 验证数据

脚本执行完成后会自动验证插入的数据，显示统计信息。

## 数据表结构

### yozuan_task_region 表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `id` | INT | 地区ID（主键，自增） | 1 |
| `region_code` | VARCHAR(6) | 地区编码（国标行政区域代码） | 110100 |
| `region_name` | VARCHAR(50) | 地区名称 | 北京城区 |
| `region_level` | VARCHAR(20) | 地区级别 | country/province/city/district |
| `parent_code` | VARCHAR(6) | 父级地区编码 | 110000 |
| `center_coords` | VARCHAR(50) | 中心坐标（经度,纬度） | 116.405285,39.904989 |
| `citycode` | VARCHAR(10) | 城市区号 | 010 |
| `status` | TINYINT | 状态（1启用，0禁用） | 1 |
| `create_time` | DATETIME | 创建时间 | 2024-01-01 00:00:00 |
| `update_time` | DATETIME | 更新时间 | 2024-01-01 00:00:00 |

### 索引设计

- `idx_region_code`: 地区编码唯一索引
- `idx_parent_code`: 父级地区编码索引
- `idx_region_level`: 地区级别索引
- `idx_status`: 状态索引
- `idx_region_hierarchy`: 地区层级复合索引
- `idx_region_composite`: 地区级别+状态复合索引
- `idx_region_name`: 地区名称索引

## 数据层级结构

```
全国 (000000, country)
├── 北京市 (110000, province)
│   └── 北京城区 (110100, city)
├── 上海市 (310000, province)
│   └── 上海城区 (310100, city)
└── 广东省 (440000, province)
    ├── 广州市 (440100, city)
    ├── 深圳市 (440300, city)
    └── 东莞市 (441900, city)
```

## API接口

### 基础接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/provinces` | GET | 获取所有省份 |
| `/cities/{province_code}` | GET | 根据省份获取城市 |
| `/tree` | GET | 获取地区树形结构 |

### 查询接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/search` | GET | 搜索地区 |
| `/info/{region_code}` | GET | 根据编码获取地区信息 |
| `/batch-info` | POST | 批量获取地区信息 |

### 统计接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/popular-cities` | GET | 获取热门城市 |
| `/statistics` | GET | 获取地区统计信息 |

## 使用示例

### 获取省份列表

```bash
curl -X GET "http://127.0.0.1:9099/yozuan/regions/provinces"
```

### 获取城市列表

```bash
curl -X GET "http://127.0.0.1:9099/yozuan/regions/cities/440000"
```

### 搜索地区

```bash
curl -X GET "http://127.0.0.1:9099/yozuan/regions/search?keyword=广州&level=city"
```

### 获取地区树形结构

```bash
curl -X GET "http://127.0.0.1:9099/yozuan/regions/tree"
```

## 注意事项

### 1. 数据完整性

- 确保 `area-city.json` 文件格式正确
- 地区编码必须符合国标行政区域代码规范
- 父子关系必须正确设置

### 2. 性能考虑

- 大量数据插入时建议在业务低峰期执行
- 已创建必要的索引优化查询性能
- 支持分页查询避免一次性返回过多数据

### 3. 数据维护

- 定期同步最新的行政区域调整数据
- 及时更新已撤销或变更的地区信息
- 保持地区编码与官方标准一致

## 错误处理

### 常见错误

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| 数据库连接失败 | 数据库配置错误 | 检查数据库连接配置 |
| 表不存在 | 未执行建表SQL | 先执行 `create_region_table.sql` |
| 数据格式错误 | JSON文件格式不正确 | 检查JSON文件格式和编码 |
| 重复数据 | 地区编码重复 | 检查数据源，确保编码唯一 |

### 调试建议

1. 检查数据库连接配置
2. 验证JSON文件格式
3. 查看详细的错误日志
4. 确认数据库权限设置

## 扩展功能

### 未来可扩展

- 支持区县级地区数据
- 添加地区经济指标
- 支持地区别名和简称
- 添加地区边界坐标数据
- 支持多语言地区名称

## 技术支持

如遇到问题，请检查：

1. 数据库连接是否正常
2. JSON文件是否完整
3. 数据库权限是否足够
4. 表结构是否正确创建

更多技术支持请参考项目文档或联系开发团队。 