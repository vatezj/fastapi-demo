-- APP用户表密码字段长度迁移脚本
-- 将password字段从varchar(50)更新为varchar(100)以支持bcrypt加密

-- MySQL版本
ALTER TABLE `app_user` MODIFY COLUMN `password` varchar(100) DEFAULT '' COMMENT '密码';

-- PostgreSQL版本（如果需要）
-- ALTER TABLE app_user ALTER COLUMN password TYPE varchar(100);
-- COMMENT ON COLUMN app_user.password IS '密码';

-- 验证更新结果
-- DESCRIBE app_user;  -- MySQL
-- \d app_user;        -- PostgreSQL
