-- APP用户相关表结构
-- 适用于 MySQL 和 PostgreSQL

-- APP用户信息表
CREATE TABLE IF NOT EXISTS `app_user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `user_name` varchar(30) NOT NULL COMMENT '用户账号',
  `nick_name` varchar(30) NOT NULL COMMENT '用户昵称',
  `email` varchar(50) DEFAULT '' COMMENT '用户邮箱',
  `phone` varchar(11) DEFAULT '' COMMENT '手机号码',
  `sex` char(1) DEFAULT '0' COMMENT '用户性别（0男 1女 2未知）',
  `avatar` varchar(100) DEFAULT '' COMMENT '用户头像',
  `password` varchar(100) DEFAULT '' COMMENT '密码',
  `status` char(1) DEFAULT '0' COMMENT '帐号状态（0正常 1停用）',
  `login_ip` varchar(128) DEFAULT '' COMMENT '最后登录IP',
  `login_date` datetime DEFAULT NULL COMMENT '最后登录时间',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='APP用户信息表';

-- APP用户详细信息表
CREATE TABLE IF NOT EXISTS `app_user_profile` (
  `profile_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '详细信息ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `real_name` varchar(30) DEFAULT '' COMMENT '真实姓名',
  `id_card` varchar(18) DEFAULT '' COMMENT '身份证号',
  `birthday` date DEFAULT NULL COMMENT '出生日期',
  `address` varchar(200) DEFAULT '' COMMENT '居住地址',
  `education` varchar(20) DEFAULT '' COMMENT '学历',
  `occupation` varchar(50) DEFAULT '' COMMENT '职业',
  `income_level` varchar(20) DEFAULT '' COMMENT '收入水平',
  `marital_status` char(1) DEFAULT '0' COMMENT '婚姻状况（0未婚 1已婚 2离异 3丧偶）',
  `emergency_contact` varchar(30) DEFAULT '' COMMENT '紧急联系人',
  `emergency_phone` varchar(11) DEFAULT '' COMMENT '紧急联系电话',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`profile_id`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  CONSTRAINT `fk_profile_user_id` FOREIGN KEY (`user_id`) REFERENCES `app_user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='APP用户详细信息表';

-- APP用户登录日志表
CREATE TABLE IF NOT EXISTS `app_login_log` (
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '访问ID',
  `user_name` varchar(50) DEFAULT '' COMMENT '用户账号',
  `ipaddr` varchar(128) DEFAULT '' COMMENT '登录IP地址',
  `login_location` varchar(255) DEFAULT '' COMMENT '登录地点',
  `browser` varchar(50) DEFAULT '' COMMENT '浏览器类型',
  `os` varchar(50) DEFAULT '' COMMENT '操作系统',
  `status` char(1) DEFAULT '0' COMMENT '登录状态（0成功 1失败）',
  `msg` varchar(255) DEFAULT '' COMMENT '提示消息',
  `login_time` datetime DEFAULT NULL COMMENT '访问时间',
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='APP用户登录日志表';

-- 插入默认数据
INSERT INTO `app_user` (`user_name`, `nick_name`, `email`, `phone`, `sex`, `avatar`, `password`, `status`, `create_time`) VALUES
('app_user1', 'APP用户1', 'app1@example.com', '13800138001', '0', '', 'e10adc3949ba59abbe56e057f20f883e', '0', NOW()),
('app_user2', 'APP用户2', 'app2@example.com', '13800138002', '1', '', 'e10adc3949ba59abbe56e057f20f883e', '0', NOW()),
('app_user3', 'APP用户3', 'app3@example.com', '13800138003', '0', '', 'e10adc3949ba59abbe56e057f20f883e', '0', NOW());

-- 插入用户详细信息
INSERT INTO `app_user_profile` (`user_id`, `real_name`, `id_card`, `birthday`, `address`, `education`, `occupation`, `income_level`, `marital_status`, `emergency_contact`, `emergency_phone`, `create_time`) VALUES
(1, '张三', '110101199001011234', '1990-01-01', '北京市朝阳区', '本科', '软件工程师', '10000-20000', '0', '李四', '13900139001', NOW()),
(2, '李四', '110101199002021234', '1990-02-02', '上海市浦东新区', '硕士', '产品经理', '20000-30000', '1', '王五', '13900139002', NOW()),
(3, '王五', '110101199003031234', '1990-03-03', '广州市天河区', '本科', '设计师', '8000-15000', '0', '赵六', '13900139003', NOW());
