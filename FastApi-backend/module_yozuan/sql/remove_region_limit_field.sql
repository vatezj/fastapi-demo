-- 移除任务表中的region_limit字段
-- 执行前请备份数据库

-- 1. 移除region_limit字段
ALTER TABLE yozuan_task DROP COLUMN region_limit;

-- 2. 验证字段已移除
DESCRIBE yozuan_task;

-- 3. 检查表结构
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'yozuan_task'
ORDER BY ORDINAL_POSITION; 