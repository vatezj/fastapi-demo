-- 游赚项目数据库建表脚本
-- 创建时间: 2025-08-15
-- 说明: 包含任务模块、账户体系、分销体系等所有相关表结构

-- =============================================
-- 1. 任务类型表
-- =============================================
CREATE TABLE yozuan_task_type (
    type_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '任务类型ID',
    type_name VARCHAR(50) NOT NULL COMMENT '任务类型名称',
    type_code VARCHAR(20) UNIQUE NOT NULL COMMENT '任务类型代码',
    min_price DECIMAL(8,2) NOT NULL COMMENT '最小单价',
    min_quantity INT NOT NULL COMMENT '最小数量',
    icon_url VARCHAR(255) COMMENT '类型图标URL',
    description TEXT COMMENT '类型描述',
    sort_order INT DEFAULT 0 COMMENT '排序权重',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
);

-- 预定义任务类型数据
INSERT INTO yozuan_task_type VALUES
(1, '推广APP', 'app_promotion', 1.00, 10, '/icons/app.png', '注册下载类任务，用户需要下载并注册指定APP', 1, 1, NOW(), NOW()),
(2, '网页注册', 'web_registration', 0.50, 20, '/icons/web.png', '网页推广任务，用户需要在指定网站完成注册', 2, 1, NOW(), NOW()),
(3, '简单帮忙', 'simple_help', 0.30, 50, '/icons/help.png', '简单操作任务，如点赞、关注、转发等', 3, 1, NOW(), NOW()),
(4, '认证绑卡', 'verification_binding', 5.00, 5, '/icons/verify.png', '身份认证任务，需要实名认证或绑定银行卡', 4, 1, NOW(), NOW()),
(5, '特单任务', 'special_task', 10.00, 3, '/icons/special.png', '证券金融类特殊任务，风险较高', 5, 1, NOW(), NOW()),
(6, '试玩应用', 'trial_app', 2.00, 15, '/icons/trial.png', '游戏试玩任务，体验指定游戏或应用', 6, 1, NOW(), NOW()),
(7, '微小程序', 'mini_program', 1.50, 25, '/icons/mini.png', '小程序推广任务，关注或使用指定小程序', 7, 1, NOW(), NOW()),
(8, '电商回收', 'ecommerce_recycle', 3.00, 8, '/icons/recycle.png', '商品回收任务，回收或转赠指定商品', 8, 1, NOW(), NOW()),
(9, '加群其它', 'group_other', 0.80, 30, '/icons/group.png', '社群推广任务，加入指定群组或关注账号', 9, 1, NOW(), NOW());

-- =============================================
-- 2. 任务标签表
-- =============================================
CREATE TABLE yozuan_task_tag (
    tag_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    tag_name VARCHAR(50) NOT NULL COMMENT '标签名称',
    tag_code VARCHAR(20) UNIQUE NOT NULL COMMENT '标签代码',
    tag_category VARCHAR(30) COMMENT '标签分类',
    description TEXT COMMENT '标签描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

-- 预定义标签数据
INSERT INTO yozuan_task_tag VALUES
(1, '电商推广', 'ecommerce', 'business', '电商平台推广任务', 1, NOW()),
(2, '金融理财', 'finance', 'finance', '金融产品推广任务', 1, NOW()),
(3, '游戏娱乐', 'game', 'entertainment', '游戏娱乐推广任务', 1, NOW()),
(4, '教育培训', 'education', 'education', '教育培训推广任务', 1, NOW()),
(5, '健康医疗', 'health', 'health', '健康医疗推广任务', 1, NOW()),
(6, '生活服务', 'lifestyle', 'lifestyle', '生活服务推广任务', 1, NOW());

-- =============================================
-- 3. 任务地区表
-- =============================================
CREATE TABLE yozuan_task_region (
    region_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区ID',
    region_code VARCHAR(10) NOT NULL COMMENT '地区代码',
    region_name VARCHAR(50) NOT NULL COMMENT '地区名称',
    parent_code VARCHAR(10) COMMENT '父级地区代码',
    region_level TINYINT DEFAULT 1 COMMENT '地区级别：1省，2市，3区',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用'
);

-- 插入基础地区数据（示例）
INSERT INTO yozuan_task_region VALUES
(1, '110000', '北京市', NULL, 1, 1),
(2, '120000', '天津市', NULL, 1, 1),
(3, '130000', '河北省', NULL, 1, 1),
(4, '310000', '上海市', NULL, 1, 1),
(5, '320000', '江苏省', NULL, 1, 1),
(6, '330000', '浙江省', NULL, 1, 1),
(7, '440000', '广东省', NULL, 1, 1),
(8, '500000', '重庆市', NULL, 1, 1),
(9, '510000', '四川省', NULL, 1, 1);

-- =============================================
-- 4. 任务主表
-- =============================================
CREATE TABLE yozuan_task (
    task_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    publisher_id INT NOT NULL COMMENT '发布者用户ID',
    task_type_id INT NOT NULL COMMENT '任务类型ID',
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    task_description TEXT COMMENT '任务详细描述',
    task_quantity INT NOT NULL COMMENT '任务总数量',
    completed_quantity INT DEFAULT 0 COMMENT '已完成数量',
    task_price DECIMAL(8,2) NOT NULL COMMENT '任务单价',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '任务总金额',
    service_fee DECIMAL(8,2) NOT NULL COMMENT '平台手续费',
    task_tag VARCHAR(50) COMMENT '推广项目标签',
    completion_hours INT NOT NULL COMMENT '报名后完成时限（小时）',
    review_hours INT NOT NULL COMMENT '验证后审核时限（小时）',
    device_limit VARCHAR(20) DEFAULT 'all' COMMENT '设备限制：all/android/ios',
    region_limit JSON COMMENT '地区限制，JSON格式存储地区代码',
    frequency_limit VARCHAR(20) DEFAULT 'once' COMMENT '限制次数：once/daily/thrice',
    task_status VARCHAR(20) DEFAULT 'draft' COMMENT '任务状态：draft/pending/active/paused/completed/cancelled',
    start_time DATETIME COMMENT '任务开始时间',
    end_time DATETIME COMMENT '任务结束时间',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_publisher (publisher_id),
    INDEX idx_type (task_type_id),
    INDEX idx_status (task_status),
    INDEX idx_create_time (create_time),
    FOREIGN KEY (publisher_id) REFERENCES app_user(user_id),
    FOREIGN KEY (task_type_id) REFERENCES yozuan_task_type(type_id)
);

-- =============================================
-- 5. 任务步骤表
-- =============================================
CREATE TABLE yozuan_task_step (
    step_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '步骤ID',
    task_id INT NOT NULL COMMENT '任务ID',
    step_order INT NOT NULL COMMENT '步骤顺序',
    step_title VARCHAR(100) NOT NULL COMMENT '步骤标题',
    step_description TEXT COMMENT '步骤描述',
    step_type VARCHAR(20) NOT NULL COMMENT '步骤类型：link/image/text',
    step_content TEXT COMMENT '步骤内容（链接、图片URL或文本）',
    is_required TINYINT DEFAULT 1 COMMENT '是否必填：1必填，0可选',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_task (task_id),
    INDEX idx_order (task_id, step_order),
    FOREIGN KEY (task_id) REFERENCES yozuan_task(task_id) ON DELETE CASCADE
);

-- =============================================
-- 6. 任务验证表
-- =============================================
CREATE TABLE yozuan_task_verification (
    verification_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '验证ID',
    task_id INT NOT NULL COMMENT '任务ID',
    verification_title VARCHAR(100) NOT NULL COMMENT '验证标题',
    verification_description TEXT COMMENT '验证说明',
    verification_type VARCHAR(20) NOT NULL COMMENT '验证类型：image/text/both',
    image_required TINYINT DEFAULT 0 COMMENT '是否需要图片：1需要，0不需要',
    text_required TINYINT DEFAULT 0 COMMENT '是否需要文本：1需要，0不需要',
    text_placeholder VARCHAR(255) COMMENT '文本输入提示',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_task (task_id),
    FOREIGN KEY (task_id) REFERENCES yozuan_task(task_id) ON DELETE CASCADE
);

-- =============================================
-- 7. 任务订单表
-- =============================================
CREATE TABLE yozuan_task_order (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    task_id INT NOT NULL COMMENT '任务ID',
    user_id INT NOT NULL COMMENT '接单用户ID',
    order_status VARCHAR(20) DEFAULT 'applied' COMMENT '订单状态：applied/in_progress/completed/verified/rejected/cancelled',
    apply_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
    start_time DATETIME COMMENT '开始时间',
    complete_time DATETIME COMMENT '完成时间',
    verify_time DATETIME COMMENT '验证时间',
    commission_amount DECIMAL(8,2) COMMENT '佣金金额',
    reject_reason TEXT COMMENT '驳回原因',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_task (task_id),
    INDEX idx_user (user_id),
    INDEX idx_status (order_status),
    INDEX idx_apply_time (apply_time),
    UNIQUE KEY uk_task_user (task_id, user_id),
    FOREIGN KEY (task_id) REFERENCES yozuan_task(task_id),
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
);

-- =============================================
-- 8. 任务验证提交表
-- =============================================
CREATE TABLE yozuan_task_verification_submit (
    submit_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '提交ID',
    order_id INT NOT NULL COMMENT '订单ID',
    submit_data JSON NOT NULL COMMENT '提交的验证数据，包含所有验证内容',
    submit_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    review_status VARCHAR(20) DEFAULT 'pending' COMMENT '审核状态：pending/approved/rejected',
    review_time DATETIME COMMENT '审核时间',
    review_user_id INT COMMENT '审核用户ID',
    review_comment TEXT COMMENT '审核意见',
    
    INDEX idx_order (order_id),
    INDEX idx_status (review_status),
    FOREIGN KEY (order_id) REFERENCES yozuan_task_order(order_id),
    FOREIGN KEY (review_user_id) REFERENCES app_user(user_id)
);

-- =============================================
-- 9. 用户账户表
-- =============================================
CREATE TABLE yozuan_user_account (
    account_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '账户ID',
    user_id INT NOT NULL COMMENT '用户ID',
    balance DECIMAL(10,2) DEFAULT 0.00 COMMENT '账户余额',
    frozen_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '冻结金额',
    total_income DECIMAL(10,2) DEFAULT 0.00 COMMENT '总收入',
    total_withdraw DECIMAL(10,2) DEFAULT 0.00 COMMENT '总提现',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_user (user_id),
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
);

-- =============================================
-- 10. 资金变动记录表
-- =============================================
CREATE TABLE yozuan_account_transaction (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '交易ID',
    account_id INT NOT NULL COMMENT '账户ID',
    transaction_type VARCHAR(20) NOT NULL COMMENT '交易类型：recharge/withdraw/task_commission/rebate/fee',
    amount DECIMAL(10,2) NOT NULL COMMENT '交易金额',
    balance_before DECIMAL(10,2) NOT NULL COMMENT '交易前余额',
    balance_after DECIMAL(10,2) NOT NULL COMMENT '交易后余额',
    description VARCHAR(255) COMMENT '交易描述',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '交易状态：pending/success/failed',
    related_id INT COMMENT '关联ID（任务ID、订单ID等）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_account (account_id),
    INDEX idx_type (transaction_type),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    FOREIGN KEY (account_id) REFERENCES yozuan_user_account(account_id)
);

-- =============================================
-- 11. 用户邀请关系表
-- =============================================
CREATE TABLE yozuan_user_invitation (
    invitation_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '邀请ID',
    inviter_id INT NOT NULL COMMENT '邀请人用户ID',
    invitee_id INT NOT NULL COMMENT '被邀请人用户ID',
    invitation_code VARCHAR(6) NOT NULL COMMENT '邀请码',
    invitation_level TINYINT DEFAULT 1 COMMENT '邀请级别：1直接邀请，2间接邀请，3三级邀请',
    parent_invitation_id INT COMMENT '上级邀请ID',
    status TINYINT DEFAULT 1 COMMENT '状态：1有效，0无效',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    UNIQUE KEY uk_invitee (invitee_id),
    INDEX idx_inviter (inviter_id),
    INDEX idx_code (invitation_code),
    INDEX idx_level (invitation_level),
    FOREIGN KEY (inviter_id) REFERENCES app_user(user_id),
    FOREIGN KEY (invitee_id) REFERENCES app_user(user_id),
    FOREIGN KEY (parent_invitation_id) REFERENCES yozuan_user_invitation(invitation_id)
);

-- =============================================
-- 12. 返佣配置表
-- =============================================
CREATE TABLE yozuan_rebate_config (
    config_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    level INT NOT NULL COMMENT '分销级别 1,2,3',
    rebate_percent DECIMAL(5,2) NOT NULL COMMENT '返佣比例',
    description VARCHAR(255) COMMENT '配置描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    UNIQUE KEY uk_level (level)
);

-- 默认返佣配置
INSERT INTO yozuan_rebate_config VALUES
(1, 1, 40.00, '一级分销返佣40%', 1, NOW()),
(2, 2, 30.00, '二级分销返佣30%', 1, NOW()),
(3, 3, 20.00, '三级分销返佣20%', 1, NOW());

-- =============================================
-- 13. 返佣记录表
-- =============================================
CREATE TABLE yozuan_rebate_record (
    record_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    inviter_id INT NOT NULL COMMENT '邀请人用户ID',
    invitee_id INT NOT NULL COMMENT '被邀请人用户ID',
    task_id INT NOT NULL COMMENT '任务ID',
    order_id INT NOT NULL COMMENT '订单ID',
    rebate_level TINYINT NOT NULL COMMENT '返佣级别：1,2,3',
    rebate_amount DECIMAL(8,2) NOT NULL COMMENT '返佣金额',
    rebate_source VARCHAR(20) DEFAULT 'task_fee' COMMENT '返佣来源：task_fee/commission',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '返佣状态：pending/success/failed',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_inviter (inviter_id),
    INDEX idx_invitee (invitee_id),
    INDEX idx_task (task_id),
    INDEX idx_order (order_id),
    INDEX idx_status (status),
    FOREIGN KEY (inviter_id) REFERENCES app_user(user_id),
    FOREIGN KEY (invitee_id) REFERENCES app_user(user_id),
    FOREIGN KEY (task_id) REFERENCES yozuan_task(task_id),
    FOREIGN KEY (order_id) REFERENCES yozuan_task_order(order_id)
);

-- =============================================
-- 14. 任务手续费配置表
-- =============================================
CREATE TABLE yozuan_task_fee_config (
    config_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    task_type_id INT COMMENT '任务类型ID，NULL表示全局配置',
    fee_type VARCHAR(20) DEFAULT 'fixed' COMMENT '手续费类型：fixed/percentage',
    fee_value DECIMAL(8,2) NOT NULL COMMENT '手续费值（固定金额或百分比）',
    min_fee DECIMAL(8,2) DEFAULT 0.00 COMMENT '最小手续费',
    max_fee DECIMAL(8,2) DEFAULT 9999.99 COMMENT '最大手续费',
    description VARCHAR(255) COMMENT '配置描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_type (task_type_id),
    FOREIGN KEY (task_type_id) REFERENCES yozuan_task_type(type_id)
);

-- 默认手续费配置
INSERT INTO yozuan_task_fee_config VALUES
(1, NULL, 'percentage', 5.00, 0.10, 100.00, '全局默认手续费5%', 1, NOW()),
(2, 1, 'fixed', 0.50, 0.50, 0.50, 'APP推广任务固定手续费0.5元', 1, NOW()),
(3, 4, 'percentage', 10.00, 1.00, 500.00, '认证绑卡任务手续费10%', 1, NOW());

-- =============================================
-- 索引优化
-- =============================================

-- 复合索引
CREATE INDEX idx_task_composite ON yozuan_task (task_type_id, task_status, create_time);
CREATE INDEX idx_order_composite ON yozuan_task_order (user_id, order_status, apply_time);
CREATE INDEX idx_transaction_composite ON yozuan_account_transaction (account_id, transaction_type, create_time);

-- 全文索引（用于任务搜索）
ALTER TABLE yozuan_task ADD FULLTEXT INDEX ft_task_search (task_name, task_description, task_tag);

-- =============================================
-- 视图创建
-- =============================================

-- 任务统计视图
CREATE VIEW yozuan_task_statistics AS
SELECT 
    t.task_id,
    t.task_name,
    t.publisher_id,
    t.task_type_id,
    tt.type_name,
    t.task_quantity,
    t.completed_quantity,
    t.task_price,
    t.total_amount,
    t.service_fee,
    t.task_status,
    t.create_time,
    COUNT(o.order_id) as total_orders,
    SUM(CASE WHEN o.order_status = 'verified' THEN 1 ELSE 0 END) as completed_orders,
    SUM(CASE WHEN o.order_status = 'rejected' THEN 1 ELSE 0 END) as rejected_orders
FROM yozuan_task t
LEFT JOIN yozuan_task_type tt ON t.task_type_id = tt.type_id
LEFT JOIN yozuan_task_order o ON t.task_id = o.task_id
GROUP BY t.task_id;

-- 用户收益统计视图
CREATE VIEW yozuan_user_earnings AS
SELECT 
    ua.user_id,
    ua.balance,
    ua.total_income,
    ua.total_withdraw,
    COUNT(t.transaction_id) as total_transactions,
    SUM(CASE WHEN t.transaction_type = 'task_commission' THEN t.amount ELSE 0 END) as total_commission,
    SUM(CASE WHEN t.transaction_type = 'rebate' THEN t.amount ELSE 0 END) as total_rebate
FROM yozuan_user_account ua
LEFT JOIN yozuan_account_transaction t ON ua.account_id = t.account_id
GROUP BY ua.user_id;

-- =============================================
-- 存储过程
-- =============================================

DELIMITER //

-- 计算任务手续费
CREATE PROCEDURE yozuan_calculate_task_fee(
    IN p_task_type_id INT,
    IN p_task_quantity INT,
    IN p_task_price DECIMAL(8,2),
    OUT p_service_fee DECIMAL(8,2)
)
BEGIN
    DECLARE v_fee_type ENUM('fixed', 'percentage');
    DECLARE v_fee_value DECIMAL(8,2);
    DECLARE v_min_fee DECIMAL(8,2);
    DECLARE v_max_fee DECIMAL(8,2);
    
    -- 获取手续费配置
    SELECT fee_type, fee_value, min_fee, max_fee 
    INTO v_fee_type, v_fee_value, v_min_fee, v_max_fee
    FROM yozuan_task_fee_config 
    WHERE (task_type_id = p_task_type_id OR task_type_id IS NULL) 
    AND status = 1 
    ORDER BY task_type_id DESC 
    LIMIT 1;
    
    -- 计算手续费
    IF v_fee_type = 'fixed' THEN
        SET p_service_fee = v_fee_value * p_task_quantity;
    ELSE
        SET p_service_fee = (p_task_price * p_task_quantity * v_fee_value) / 100;
    END IF;
    
    -- 应用最小最大限制
    SET p_service_fee = GREATEST(p_service_fee, v_min_fee);
    SET p_service_fee = LEAST(p_service_fee, v_max_fee);
    
    -- 四舍五入到2位小数
    SET p_service_fee = ROUND(p_service_fee, 2);
END //

-- 分配任务返佣
CREATE PROCEDURE yozuan_distribute_task_rebate(
    IN p_task_id INT,
    IN p_order_id INT,
    IN p_service_fee DECIMAL(8,2)
)
BEGIN
    DECLARE v_invitation_id INT;
    DECLARE v_inviter_id INT;
    DECLARE v_rebate_level INT;
    DECLARE v_rebate_percent DECIMAL(5,2);
    DECLARE v_rebate_amount DECIMAL(8,2);
    DECLARE v_done INT DEFAULT FALSE;
    
    -- 获取订单用户信息
    SELECT user_id INTO v_invitation_id FROM yozuan_task_order WHERE order_id = p_order_id;
    
    -- 遍历邀请链分配返佣
    rebate_loop: LOOP
        -- 获取上级邀请人
        SELECT inviter_id, invitation_level 
        INTO v_inviter_id, v_rebate_level
        FROM yozuan_user_invitation 
        WHERE invitee_id = v_invitation_id AND status = 1;
        
        IF v_inviter_id IS NULL OR v_rebate_level > 3 THEN
            LEAVE rebate_loop;
        END IF;
        
        -- 获取返佣比例
        SELECT rebate_percent INTO v_rebate_percent
        FROM yozuan_rebate_config 
        WHERE level = v_rebate_level AND status = 1;
        
        IF v_rebate_percent IS NOT NULL THEN
            -- 计算返佣金额
            SET v_rebate_amount = (p_service_fee * v_rebate_percent) / 100;
            
            -- 插入返佣记录
            INSERT INTO yozuan_rebate_record (
                inviter_id, invitee_id, task_id, order_id, 
                rebate_level, rebate_amount, rebate_source, status
            ) VALUES (
                v_inviter_id, v_invitation_id, p_task_id, p_order_id,
                v_rebate_level, v_rebate_amount, 'task_fee', 'pending'
            );
            
            -- 更新用户账户（这里需要调用账户更新逻辑）
            -- CALL yozuan_update_user_balance(v_inviter_id, v_rebate_amount, 'rebate');
        END IF;
        
        -- 移动到上级
        SET v_invitation_id = v_inviter_id;
    END LOOP;
END //

DELIMITER ;

-- =============================================
-- 触发器
-- =============================================

-- 任务订单状态变更触发器
DELIMITER //
CREATE TRIGGER yozuan_task_order_status_trigger
AFTER UPDATE ON yozuan_task_order
FOR EACH ROW
BEGIN
    IF NEW.order_status = 'verified' AND OLD.order_status != 'verified' THEN
        -- 任务验证通过，更新任务完成数量
        UPDATE yozuan_task 
        SET completed_quantity = completed_quantity + 1,
            update_time = NOW()
        WHERE task_id = NEW.task_id;
        
        -- 检查任务是否完成
        UPDATE yozuan_task 
        SET task_status = 'completed',
            update_time = NOW()
        WHERE task_id = NEW.task_id 
        AND completed_quantity >= task_quantity;
    END IF;
END //
DELIMITER ;

-- 账户交易触发器
DELIMITER //
CREATE TRIGGER yozuan_account_transaction_trigger
AFTER INSERT ON yozuan_account_transaction
FOR EACH ROW
BEGIN
    IF NEW.status = 'success' THEN
        -- 更新账户余额
        UPDATE yozuan_user_account 
        SET balance = NEW.balance_after,
            update_time = NOW()
        WHERE account_id = NEW.account_id;
        
        -- 更新总收入
        IF NEW.transaction_type IN ('task_commission', 'rebate') THEN
            UPDATE yozuan_user_account 
            SET total_income = total_income + NEW.amount,
                update_time = NOW()
            WHERE account_id = NEW.account_id;
        END IF;
        
        -- 更新总提现
        IF NEW.transaction_type = 'withdraw' THEN
            UPDATE yozuan_user_account 
            SET total_withdraw = total_withdraw + NEW.amount,
                update_time = NOW()
            WHERE account_id = NEW.account_id;
        END IF;
    END IF;
END //
DELIMITER ;

-- =============================================
-- 数据初始化
-- =============================================

-- 为现有用户创建账户（如果有的话）
-- INSERT INTO yozuan_user_account (user_id, balance, frozen_amount, total_income, total_withdraw)
-- SELECT user_id, 0.00, 0.00, 0.00, 0.00 FROM app_user 
-- WHERE user_id NOT IN (SELECT user_id FROM yozuan_user_account);

-- =============================================
-- 示例数据：展示一个任务可以有多个步骤和多个验证
-- =============================================

-- 示例：创建一个APP推广任务
-- INSERT INTO yozuan_task VALUES
-- (1, 1, 1, '下载并注册某金融APP', '完成APP下载、注册、实名认证等步骤', 100, 0, 2.00, 200.00, 10.00, '金融理财', 24, 12, 'all', '["110000", "120000"]', 'once', 'active', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), NOW(), NOW());

-- 示例：该任务的多个步骤
-- INSERT INTO yozuan_task_step VALUES
-- (1, 1, 1, '下载APP', '从应用商店下载指定APP', 'link', 'https://example.com/download', 1, NOW()),
-- (2, 1, 2, '注册账号', '使用手机号注册新账号', 'text', '请填写注册信息截图', 1, NOW()),
-- (3, 1, 3, '实名认证', '完成身份信息认证', 'image', '请上传身份证正反面照片', 1, NOW()),
-- (4, 1, 4, '绑定银行卡', '绑定一张银行卡', 'image', '请上传银行卡绑定成功截图', 1, NOW());

-- 示例：该任务的多个验证要求
-- INSERT INTO yozuan_task_verification VALUES
-- (1, 1, '注册完成验证', '请提供注册成功的截图', 'image', 1, 0, NULL, NOW()),
-- (2, 1, '实名认证验证', '请提供实名认证通过的截图', 'image', 1, 0, NULL, NOW()),
-- (3, 1, '银行卡绑定验证', '请提供银行卡绑定成功的截图', 'image', 1, 0, NULL, NOW()),
-- (4, 1, '任务完成确认', '请描述完成任务的感受', 'text', 0, 1, '请简单描述使用体验', NOW());

-- 示例：用户接单并提交验证
-- INSERT INTO yozuan_task_order VALUES
-- (1, 1, 2, 'completed', NOW(), DATE_ADD(NOW(), INTERVAL 1 HOUR), DATE_ADD(NOW(), INTERVAL 2 HOUR), NULL, 2.00, NULL, NOW(), NOW());

-- 示例：用户一次性提交所有验证内容
-- INSERT INTO yozuan_task_verification_submit VALUES
-- (1, 1, '{"verifications": [{"verification_id": 1, "images": ["uploads/verify1.jpg", "uploads/verify2.jpg"]}, {"verification_id": 2, "images": ["uploads/verify3.jpg"]}, {"verification_id": 3, "images": ["uploads/verify4.jpg"]}, {"verification_id": 4, "text": "APP界面简洁，操作流畅，功能齐全，整体体验不错"}]}', DATE_ADD(NOW(), INTERVAL 2 HOUR), 'pending', NULL, NULL, NULL);

-- =============================================
-- 注释说明
-- =============================================

/*
游赚项目数据库设计说明：

1. 表命名规范：所有表名以 yozuan_ 开头，便于识别和管理
2. 外键约束：使用外键确保数据完整性
3. 索引优化：为常用查询字段建立索引，提高查询性能
4. 视图：创建统计视图，简化复杂查询
5. 存储过程：封装业务逻辑，如手续费计算和返佣分配
6. 触发器：自动维护数据一致性，如订单状态变更和账户余额更新

主要业务流程：
1. 用户发布任务 -> 支付手续费 -> 任务上线
2. 用户报名任务 -> 执行任务 -> 提交验证
3. 发布者审核 -> 通过则分配佣金和返佣
4. 系统自动计算并分配各级分销返佣

注意事项：
1. 所有金额字段使用 DECIMAL 类型，确保精度
2. 状态字段使用 ENUM 类型，限制可选值
3. 时间字段统一使用 DATETIME 类型
4. 重要操作需要记录日志和审计信息
*/
