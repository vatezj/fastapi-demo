-- 游赚模块地区表结构
-- 用于优化任务地区存储和查询

-- 地区表
CREATE TABLE IF NOT EXISTS `yozuan_region` (
    `region_code` VARCHAR(6) PRIMARY KEY COMMENT '地区编码',
    `region_name` VARCHAR(50) NOT NULL COMMENT '地区名称',
    `region_level` ENUM('country','province','city','county') NOT NULL COMMENT '地区级别',
    `parent_code` VARCHAR(6) COMMENT '上级地区编码',
    `full_name` VARCHAR(200) COMMENT '完整地区名称路径',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地区表';

-- 任务地区关联表
CREATE TABLE IF NOT EXISTS `yozuan_task_region` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    `task_id` BIGINT NOT NULL COMMENT '任务ID',
    `region_code` VARCHAR(6) NOT NULL COMMENT '地区编码',
    `region_level` ENUM('country','province','city','county') NOT NULL COMMENT '地区级别',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务地区关联表';

-- 创建索引
CREATE INDEX `idx_parent_code` ON `yozuan_region` (`parent_code`);
CREATE INDEX `idx_region_level` ON `yozuan_region` (`region_level`);
CREATE INDEX `idx_status` ON `yozuan_region` (`status`);
CREATE INDEX `idx_sort_order` ON `yozuan_region` (`sort_order`);

CREATE INDEX `idx_task_id` ON `yozuan_task_region` (`task_id`);
CREATE INDEX `idx_region_code` ON `yozuan_task_region` (`region_code`);
CREATE INDEX `idx_region_level` ON `yozuan_task_region` (`region_level`);
CREATE INDEX `idx_task_region_composite` ON `yozuan_task_region` (`task_id`, `region_code`, `region_level`);

-- 防止重复关联
ALTER TABLE `yozuan_task_region` ADD UNIQUE KEY `uk_task_region` (`task_id`, `region_code`);

-- 插入基础地区数据
INSERT INTO `yozuan_region` (`region_code`, `region_name`, `region_level`, `parent_code`, `full_name`, `sort_order`, `status`) VALUES
-- 国家级
('000000', '全国', 'country', NULL, '全国', 0, 1),
('999999', '海外', 'country', NULL, '海外', 999, 1),
('888888', '不限地区', 'country', NULL, '不限地区', 888, 1),

-- 省级
('11', '北京市', 'province', '000000', '北京市', 1, 1),
('12', '天津市', 'province', '000000', '天津市', 2, 1),
('13', '河北省', 'province', '000000', '河北省', 3, 1),
('14', '山西省', 'province', '000000', '山西省', 4, 1),
('15', '内蒙古自治区', 'province', '000000', '内蒙古自治区', 5, 1),
('21', '辽宁省', 'province', '000000', '辽宁省', 6, 1),
('22', '吉林省', 'province', '000000', '吉林省', 7, 1),
('23', '黑龙江省', 'province', '000000', '黑龙江省', 8, 1),
('31', '上海市', 'province', '000000', '上海市', 9, 1),
('32', '江苏省', 'province', '000000', '江苏省', 10, 1),
('33', '浙江省', 'province', '000000', '浙江省', 11, 1),
('34', '安徽省', 'province', '000000', '安徽省', 12, 1),
('35', '福建省', 'province', '000000', '福建省', 13, 1),
('36', '江西省', 'province', '000000', '江西省', 14, 1),
('37', '山东省', 'province', '000000', '山东省', 15, 1),
('41', '河南省', 'province', '000000', '河南省', 16, 1),
('42', '湖北省', 'province', '000000', '湖北省', 17, 1),
('43', '湖南省', 'province', '000000', '湖南省', 18, 1),
('44', '广东省', 'province', '000000', '广东省', 19, 1),
('45', '广西壮族自治区', 'province', '000000', '广西壮族自治区', 20, 1),
('46', '海南省', 'province', '000000', '海南省', 21, 1),
('50', '重庆市', 'province', '000000', '重庆市', 22, 1),
('51', '四川省', 'province', '000000', '四川省', 23, 1),
('52', '贵州省', 'province', '000000', '贵州省', 24, 1),
('53', '云南省', 'province', '000000', '云南省', 25, 1),
('54', '西藏自治区', 'province', '000000', '西藏自治区', 26, 1),
('61', '陕西省', 'province', '000000', '陕西省', 27, 1),
('62', '甘肃省', 'province', '000000', '甘肃省', 28, 1),
('63', '青海省', 'province', '000000', '青海省', 29, 1),
('64', '宁夏回族自治区', 'province', '000000', '宁夏回族自治区', 30, 1),
('65', '新疆维吾尔自治区', 'province', '000000', '新疆维吾尔自治区', 31, 1),

-- 市级示例（以北京为例）
('1101', '北京市市辖区', 'city', '11', '北京市市辖区', 1, 1),
('1102', '北京市县', 'city', '11', '北京市县', 2, 1),

-- 县级示例（以北京为例）
('110101', '东城区', 'county', '1101', '北京市东城区', 1, 1),
('110102', '西城区', 'county', '1101', '北京市西城区', 2, 1),
('110105', '朝阳区', 'county', '1101', '北京市朝阳区', 3, 1),
('110106', '丰台区', 'county', '1101', '北京市丰台区', 4, 1),
('110107', '石景山区', 'county', '1101', '北京市石景山区', 5, 1),
('110108', '海淀区', 'county', '1101', '北京市海淀区', 6, 1),
('110109', '门头沟区', 'county', '1101', '北京市门头沟区', 7, 1),
('110111', '房山区', 'county', '1101', '北京市房山区', 8, 1),
('110112', '通州区', 'county', '1101', '北京市通州区', 9, 1),
('110113', '顺义区', 'county', '1101', '北京市顺义区', 10, 1),
('110114', '昌平区', 'county', '1101', '北京市昌平区', 11, 1),
('110115', '大兴区', 'county', '1101', '北京市大兴区', 12, 1),
('110116', '怀柔区', 'county', '1101', '北京市怀柔区', 13, 1),
('110117', '平谷区', 'county', '1101', '北京市平谷区', 14, 1),
('110118', '密云区', 'county', '1101', '北京市密云区', 15, 1),
('110119', '延庆区', 'county', '1101', '北京市延庆区', 16, 1),

-- 上海市级
('3101', '上海市市辖区', 'city', '31', '上海市市辖区', 1, 1),

-- 上海县级
('310101', '黄浦区', 'county', '3101', '上海市黄浦区', 1, 1),
('310104', '徐汇区', 'county', '3101', '上海市徐汇区', 2, 1),
('310105', '长宁区', 'county', '3101', '上海市长宁区', 3, 1),
('310106', '静安区', 'county', '3101', '上海市静安区', 4, 1),
('310107', '普陀区', 'county', '3101', '上海市普陀区', 5, 1),
('310109', '虹口区', 'county', '3101', '上海市虹口区', 6, 1),
('310110', '杨浦区', 'county', '3101', '上海市杨浦区', 7, 1),
('310112', '闵行区', 'county', '3101', '上海市闵行区', 8, 1),
('310113', '宝山区', 'county', '3101', '上海市宝山区', 9, 1),
('310114', '嘉定区', 'county', '3101', '上海市嘉定区', 10, 1),
('310115', '浦东新区', 'county', '3101', '上海市浦东新区', 11, 1),
('310116', '金山区', 'county', '3101', '上海市金山区', 12, 1),
('310117', '松江区', 'county', '3101', '上海市松江区', 13, 1),
('310118', '青浦区', 'county', '3101', '上海市青浦区', 14, 1),
('310120', '奉贤区', 'county', '3101', '上海市奉贤区', 15, 1),
('310151', '崇明区', 'county', '3101', '上海市崇明区', 16, 1);

-- 创建视图：任务地区信息视图
CREATE OR REPLACE VIEW `v_yozuan_task_region_info` AS
SELECT 
    tr.id,
    tr.task_id,
    tr.region_code,
    tr.region_level,
    r.region_name,
    r.full_name,
    r.parent_code,
    tr.create_time
FROM yozuan_task_region tr
JOIN yozuan_region r ON tr.region_code = r.region_code
WHERE r.status = 1;

-- 创建存储过程：获取地区层级路径
DELIMITER //
CREATE PROCEDURE `sp_get_region_path`(IN region_code VARCHAR(6))
BEGIN
    WITH RECURSIVE region_path AS (
        SELECT region_code, region_name, parent_code, full_name, 1 as level
        FROM yozuan_region 
        WHERE region_code = region_code
        
        UNION ALL
        
        SELECT r.region_code, r.region_name, r.parent_code, r.full_name, rp.level + 1
        FROM yozuan_region r
        JOIN region_path rp ON r.region_code = rp.parent_code
        WHERE rp.level < 4
    )
    SELECT * FROM region_path ORDER BY level DESC;
END //
DELIMITER ;
