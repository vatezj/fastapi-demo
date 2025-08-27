-- 创建任务地区表
-- 用于存储全国各省市地区信息

CREATE TABLE IF NOT EXISTS yozuan_task_region (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区ID',
    region_code VARCHAR(6) NOT NULL UNIQUE COMMENT '地区编码（国标行政区域代码）',
    region_name VARCHAR(50) NOT NULL COMMENT '地区名称',
    region_level VARCHAR(20) NOT NULL COMMENT '地区级别（country/province/city/district）',
    parent_code VARCHAR(6) COMMENT '父级地区编码',
    center_coords VARCHAR(50) COMMENT '中心坐标（经度,纬度）',
    citycode VARCHAR(10) COMMENT '城市区号',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_region_code (region_code),
    INDEX idx_parent_code (parent_code),
    INDEX idx_region_level (region_level),
    INDEX idx_status (status),
    INDEX idx_region_hierarchy (parent_code, region_level)
) COMMENT '任务地区表';

-- 插入全国数据
INSERT INTO yozuan_task_region (region_code, region_name, region_level, parent_code, center_coords, citycode, status) 
VALUES ('000000', '全国', 'country', NULL, NULL, NULL, 1)
ON DUPLICATE KEY UPDATE region_name = VALUES(region_name);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_region_composite ON yozuan_task_region (region_level, status);
CREATE INDEX IF NOT EXISTS idx_region_name ON yozuan_task_region (region_name); 