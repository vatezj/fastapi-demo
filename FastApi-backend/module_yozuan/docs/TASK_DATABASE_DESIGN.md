# 游赚项目任务模块数据库设计

## 📋 表命名规范

所有表名添加 `yozuan_` 前缀，便于识别和管理。

## 🗄️ 核心表结构设计

### 1. 任务类型表 (yozuan_task_type)
```sql
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
```

### 2. 任务主表 (yozuan_task)
```sql
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
```

### 3. 任务步骤表 (yozuan_task_step)
```sql
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
```

### 4. 任务验证表 (yozuan_task_verification)
```sql
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
```

### 5. 任务订单表 (yozuan_task_order)
```sql
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
```

### 6. 任务验证提交表 (yozuan_task_verification_submit)
```sql
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
```

**说明**: 验证提交是一次性提交所有验证内容，`submit_data` 字段存储JSON格式的验证数据，包含所有验证要求的内容。

### 7. 任务标签表 (yozuan_task_tag)
```sql
CREATE TABLE yozuan_task_tag (
    tag_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    tag_name VARCHAR(50) NOT NULL COMMENT '标签名称',
    tag_code VARCHAR(20) UNIQUE NOT NULL COMMENT '标签代码',
    tag_category VARCHAR(30) COMMENT '标签分类',
    description TEXT COMMENT '标签描述',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_category (tag_category),
    INDEX idx_status (status)
);

-- 预定义标签数据
INSERT INTO yozuan_task_tag VALUES
(1, '电商推广', 'ecommerce', 'business', '电商平台推广任务', 1, NOW()),
(2, '金融理财', 'finance', 'finance', '金融产品推广任务', 1, NOW()),
(3, '游戏娱乐', 'game', 'entertainment', '游戏娱乐推广任务', 1, NOW()),
(4, '教育培训', 'education', 'education', '教育培训推广任务', 1, NOW()),
(5, '健康医疗', 'health', 'health', '健康医疗推广任务', 1, NOW()),
(6, '生活服务', 'lifestyle', 'lifestyle', '生活服务推广任务', 1, NOW());
```

### 8. 任务地区表 (yozuan_task_region)
```sql
CREATE TABLE yozuan_task_region (
    region_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区ID',
    region_code VARCHAR(10) NOT NULL COMMENT '地区代码',
    region_name VARCHAR(50) NOT NULL COMMENT '地区名称',
    parent_code VARCHAR(10) COMMENT '父级地区代码',
    region_level TINYINT DEFAULT 1 COMMENT '地区级别：1省，2市，3区',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
    
    INDEX idx_code (region_code),
    INDEX idx_parent (parent_code),
    INDEX idx_level (region_level)
);
```

## 🔌 接口设计

### 任务管理接口

#### 1. 任务类型接口
```
GET /yozuan/v1/task/types - 获取任务类型列表
GET /yozuan/v1/task/types/{type_id} - 获取任务类型详情
POST /yozuan/v1/admin/task/types - 创建任务类型（管理员）
PUT /yozuan/v1/admin/task/types/{type_id} - 更新任务类型（管理员）
DELETE /yozuan/v1/admin/task/types/{type_id} - 删除任务类型（管理员）
```

#### 2. 任务发布接口
```
POST /yozuan/v1/task - 发布任务
GET /yozuan/v1/task - 获取任务列表
GET /yozuan/v1/task/{task_id} - 获取任务详情
PUT /yozuan/v1/task/{task_id} - 更新任务
DELETE /yozuan/v1/task/{task_id} - 删除任务
POST /yozuan/v1/task/{task_id}/pause - 暂停任务
POST /yozuan/v1/task/{task_id}/resume - 恢复任务
POST /yozuan/v1/task/{task_id}/cancel - 取消任务
```

#### 3. 任务接单接口
```
POST /yozuan/v1/task/{task_id}/apply - 报名任务
GET /yozuan/v1/task/orders - 获取我的任务订单
GET /yozuan/v1/task/orders/{order_id} - 获取订单详情
POST /yozuan/v1/task/orders/{order_id}/start - 开始任务
POST /yozuan/v1/task/orders/{order_id}/complete - 完成任务
POST /yozuan/v1/task/orders/{order_id}/cancel - 取消任务
```

#### 4. 任务验证接口
```
POST /yozuan/v1/task/orders/{order_id}/verify - 提交任务验证
GET /yozuan/v1/task/orders/{order_id}/verification - 获取验证详情
PUT /yozuan/v1/task/orders/{order_id}/verification - 更新验证内容
```

#### 5. 任务审核接口
```
GET /yozuan/v1/task/publisher/orders - 获取发布的任务订单
POST /yozuan/v1/task/orders/{order_id}/approve - 审核通过
POST /yozuan/v1/task/orders/{order_id}/reject - 审核驳回
GET /yozuan/v1/task/publisher/statistics - 获取发布者统计
```

#### 6. 任务搜索和筛选接口
```
GET /yozuan/v1/task/search - 搜索任务
GET /yozuan/v1/task/filter - 筛选任务
GET /yozuan/v1/task/recommend - 推荐任务
GET /yozuan/v1/task/hot - 热门任务
```

## 📊 数据关系图

```
yozuan_task_type (任务类型)
       ↓
yozuan_task (任务主表)
       ↓
├── yozuan_task_step (任务步骤) ← 1:N 关系，一个任务可以有多个步骤
├── yozuan_task_verification (任务验证) ← 1:N 关系，一个任务可以有多个验证要求
└── yozuan_task_order (任务订单) ← 1:N 关系，一个任务可以有多个订单
            ↓
yozuan_task_verification_submit (验证提交) ← 一次性提交所有验证内容

yozuan_task_tag (任务标签) ←→ yozuan_task (多对多)
yozuan_task_region (地区) ←→ yozuan_task (多对多)
```

### 关系说明
- **任务与步骤**: 一对多关系，一个任务可以有多个步骤，步骤按顺序执行
- **任务与验证**: 一对多关系，一个任务可以有多个验证要求，用户需要全部完成
- **任务与订单**: 一对多关系，一个任务可以被多个用户接单
- **验证与提交**: 一次性提交关系，用户一次性提交所有验证内容，审核时整体通过或驳回

## 🔧 索引优化建议

### 主要查询索引
- `yozuan_task`: (publisher_id, task_status, create_time)
- `yozuan_task_order`: (task_id, user_id, order_status)
- `yozuan_task_verification_submit`: (order_id, review_status)

### 复合索引
- `yozuan_task`: (task_type_id, task_status, region_limit)
- `yozuan_task_order`: (user_id, order_status, apply_time)

## 📝 注意事项

1. **数据一致性**: 使用外键约束确保数据完整性
2. **性能优化**: 对常用查询字段建立索引
3. **扩展性**: 预留字段和表结构便于功能扩展
4. **安全性**: 敏感操作需要权限验证
5. **监控**: 记录关键操作日志便于问题排查
