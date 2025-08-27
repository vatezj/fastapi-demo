-- 更新任务表，添加地区范围类型字段
-- 执行前请备份数据库

-- 1. 添加地区范围类型字段
ALTER TABLE yozuan_task 
ADD COLUMN area_scope TINYINT DEFAULT 1 COMMENT '地区范围类型：1=全国，2=单个城市，3=多个城市' AFTER device_limit;

-- 2. 添加单个城市编码字段
ALTER TABLE yozuan_task 
ADD COLUMN single_area_code VARCHAR(6) COMMENT '单个城市编码（仅当area_scope=2时有效）' AFTER area_scope;

-- 3. 创建任务城市关联表
CREATE TABLE IF NOT EXISTS yozuan_task_city_rel (
    rel_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关联ID',
    task_id INT NOT NULL COMMENT '任务ID',
    area_code VARCHAR(6) NOT NULL COMMENT '城市编码',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_task_city (task_id, area_code),
    INDEX idx_area_code (area_code)
) COMMENT '任务城市关联表';

-- 4. 为现有任务设置默认地区范围类型
-- 如果region_limit字段包含多个地区，设置为多城市类型
UPDATE yozuan_task 
SET area_scope = 3 
WHERE JSON_LENGTH(region_limit) > 1;

-- 如果region_limit字段包含单个地区且不是全国，设置为单城市类型
UPDATE yozuan_task 
SET area_scope = 2, single_area_code = JSON_UNQUOTE(JSON_EXTRACT(region_limit, '$[0].region_code'))
WHERE JSON_LENGTH(region_limit) = 1 
AND JSON_UNQUOTE(JSON_EXTRACT(region_limit, '$[0].region_code')) != '000000';

-- 5. 创建索引优化查询性能
CREATE INDEX idx_task_area_scope ON yozuan_task (area_scope);
CREATE INDEX idx_task_single_area ON yozuan_task (area_scope, single_area_code);
CREATE INDEX idx_rel_task_area ON yozuan_task_city_rel (task_id, area_code); 