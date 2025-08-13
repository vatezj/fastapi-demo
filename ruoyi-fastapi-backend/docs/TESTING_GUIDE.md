# 测试指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的测试策略和实现方法，包括单元测试、集成测试、性能测试等。

## 测试策略

### 1. 测试金字塔

```
    ┌─────────────┐
    │    E2E      │  ← 端到端测试 (少量)
    ├─────────────┤
    │ Integration │  ← 集成测试 (中等)
    ├─────────────┤
    │    Unit     │  ← 单元测试 (大量)
    └─────────────┘
```

### 2. 测试类型

- **单元测试**: 测试单个函数或方法
- **集成测试**: 测试模块间交互
- **接口测试**: 测试API接口功能
- **性能测试**: 测试系统性能指标

## 测试环境配置

### 1. 依赖安装

```bash
# 安装测试依赖
pip install pytest
pip install pytest-asyncio
pip install pytest-cov
pip install httpx
pip install factory-boy
pip install faker
```

### 2. 测试配置

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
    api: API测试
```

## 单元测试

### 1. 基础测试结构

```python
# tests/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from module_admin.service.user_service import UserService
from module_admin.entity.do.user_do import UserDO

class TestUserService:
    """用户服务测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.user_service = UserService()
        self.mock_user_dao = Mock()
        self.user_service.user_dao = self.mock_user_dao
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass
    
    @pytest.mark.unit
    def test_get_user_by_id_success(self):
        """测试根据ID获取用户成功"""
        # 准备测试数据
        user_id = 1
        expected_user = UserDO(
            id=1,
            username="testuser",
            email="test@example.com"
        )
        
        # 模拟DAO层返回
        self.mock_user_dao.get_by_id.return_value = expected_user
        
        # 执行测试
        result = self.user_service.get_user_by_id(user_id)
        
        # 验证结果
        assert result is not None
        assert result.id == user_id
        assert result.username == "testuser"
        
        # 验证DAO方法被调用
        self.mock_user_dao.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.unit
    def test_get_user_by_id_not_found(self):
        """测试根据ID获取用户不存在"""
        # 准备测试数据
        user_id = 999
        
        # 模拟DAO层返回None
        self.mock_user_dao.get_by_id.return_value = None
        
        # 执行测试
        result = self.user_service.get_user_by_id(user_id)
        
        # 验证结果
        assert result is None
        
        # 验证DAO方法被调用
        self.mock_user_dao.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.unit
    def test_create_user_success(self):
        """测试创建用户成功"""
        # 准备测试数据
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
        
        expected_user = UserDO(
            id=1,
            username="newuser",
            email="new@example.com"
        )
        
        # 模拟DAO层返回
        self.mock_user_dao.create.return_value = expected_user
        
        # 执行测试
        result = self.user_service.create_user(user_data)
        
        # 验证结果
        assert result is not None
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        
        # 验证DAO方法被调用
        self.mock_user_dao.create.assert_called_once()
```

### 2. 异步测试

```python
# tests/test_async_user_service.py
import pytest
import asyncio
from unittest.mock import AsyncMock
from module_admin.service.user_service import UserService

class TestAsyncUserService:
    """异步用户服务测试类"""
    
    @pytest.fixture
    async def user_service(self):
        """创建用户服务实例"""
        service = UserService()
        service.user_dao = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_id_async(self, user_service):
        """测试异步获取用户"""
        # 准备测试数据
        user_id = 1
        expected_user = UserDO(
            id=1,
            username="testuser",
            email="test@example.com"
        )
        
        # 模拟异步DAO层返回
        user_service.user_dao.get_by_id.return_value = expected_user
        
        # 执行测试
        result = await user_service.get_user_by_id(user_id)
        
        # 验证结果
        assert result is not None
        assert result.id == user_id
        
        # 验证DAO方法被调用
        user_service.user_dao.get_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_users_batch(self, user_service):
        """测试批量获取用户"""
        # 准备测试数据
        user_ids = [1, 2, 3]
        expected_users = [
            UserDO(id=1, username="user1"),
            UserDO(id=2, username="user2"),
            UserDO(id=3, username="user3")
        ]
        
        # 模拟异步DAO层返回
        user_service.user_dao.get_by_ids.return_value = expected_users
        
        # 执行测试
        result = await user_service.get_users_by_ids(user_ids)
        
        # 验证结果
        assert len(result) == 3
        assert result[0].username == "user1"
        
        # 验证DAO方法被调用
        user_service.user_dao.get_by_ids.assert_called_once_with(user_ids)
```

### 3. 参数化测试

```python
# tests/test_user_validation.py
import pytest
from module_admin.service.user_service import UserService

class TestUserValidation:
    """用户验证测试类"""
    
    @pytest.fixture
    def user_service(self):
        """创建用户服务实例"""
        return UserService()
    
    @pytest.mark.parametrize("username,expected", [
        ("validuser", True),
        ("user123", True),
        ("", False),
        ("a" * 51, False),  # 超过50字符
        ("user@name", False),  # 包含特殊字符
        ("123user", True),
    ])
    def test_validate_username(self, user_service, username, expected):
        """测试用户名验证"""
        result = user_service.validate_username(username)
        assert result == expected
    
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("user.name@domain.co.uk", True),
        ("invalid-email", False),
        ("@domain.com", False),
        ("user@", False),
        ("", False),
    ])
    def test_validate_email(self, user_service, email, expected):
        """测试邮箱验证"""
        result = user_service.validate_email(email)
        assert result == expected
    
    @pytest.mark.parametrize("password,expected", [
        ("Password123!", True),
        ("weak", False),
        ("12345678", False),
        ("password123", False),
        ("PASSWORD123", False),
        ("Pass123", False),
    ])
    def test_validate_password_strength(self, user_service, password, expected):
        """测试密码强度验证"""
        result = user_service.validate_password_strength(password)
        assert result == expected
```

## 集成测试

### 1. 数据库集成测试

```python
# tests/test_user_integration.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from module_admin.service.user_service import UserService
from module_admin.dao.user_dao import UserDAO
from module_admin.entity.do.user_do import UserDO

class TestUserIntegration:
    """用户集成测试类"""
    
    @pytest.fixture(scope="class")
    async def engine(self):
        """创建测试数据库引擎"""
        # 使用测试数据库
        test_db_url = "sqlite+aiosqlite:///./test.db"
        engine = create_async_engine(test_db_url, echo=True)
        
        # 创建表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        
        # 清理
        await engine.dispose()
    
    @pytest.fixture
    async def session(self, engine):
        """创建测试会话"""
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    
    @pytest.fixture
    async def user_service(self, session):
        """创建用户服务实例"""
        user_dao = UserDAO(session)
        return UserService(user_dao)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_get_user(self, user_service, session):
        """测试创建和获取用户"""
        # 准备测试数据
        user_data = {
            "username": "integration_user",
            "email": "integration@example.com",
            "password": "password123"
        }
        
        # 创建用户
        created_user = await user_service.create_user(user_data)
        assert created_user is not None
        assert created_user.username == "integration_user"
        
        # 获取用户
        retrieved_user = await user_service.get_user_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "integration_user"
        assert retrieved_user.email == "integration@example.com"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_update(self, user_service, session):
        """测试用户更新"""
        # 创建用户
        user_data = {
            "username": "update_user",
            "email": "update@example.com",
            "password": "password123"
        }
        user = await user_service.create_user(user_data)
        
        # 更新用户
        update_data = {"email": "updated@example.com"}
        updated_user = await user_service.update_user(user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.email == "updated@example.com"
        
        # 验证数据库中的更新
        retrieved_user = await user_service.get_user_by_id(user.id)
        assert retrieved_user.email == "updated@example.com"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_delete(self, user_service, session):
        """测试用户删除"""
        # 创建用户
        user_data = {
            "username": "delete_user",
            "email": "delete@example.com",
            "password": "password123"
        }
        user = await user_service.create_user(user_data)
        
        # 删除用户
        result = await user_service.delete_user(user.id)
        assert result is True
        
        # 验证用户已被删除
        deleted_user = await user_service.get_user_by_id(user.id)
        assert deleted_user is None
```

### 2. API集成测试

```python
# tests/test_user_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app import app

class TestUserAPI:
    """用户API测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """创建异步测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.api
    def test_get_user_list(self, client):
        """测试获取用户列表"""
        response = client.get("/user/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "code" in data
        assert data["code"] == 200
    
    @pytest.mark.api
    def test_create_user(self, client):
        """测试创建用户"""
        user_data = {
            "username": "api_user",
            "email": "api@example.com",
            "password": "password123"
        }
        
        response = client.post("/user/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == 200
        assert "用户创建成功" in data["msg"]
    
    @pytest.mark.api
    def test_create_user_validation_error(self, client):
        """测试创建用户验证错误"""
        # 缺少必填字段
        user_data = {
            "username": "api_user"
            # 缺少email和password
        }
        
        response = client.post("/user/", json=user_data)
        assert response.status_code == 422  # 验证错误
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_user_by_id_async(self, async_client):
        """测试异步获取用户"""
        # 先创建用户
        user_data = {
            "username": "async_user",
            "email": "async@example.com",
            "password": "password123"
        }
        
        create_response = await async_client.post("/user/", json=user_data)
        assert create_response.status_code == 200
        
        # 获取用户ID
        create_data = create_response.json()
        user_id = create_data["data"]["id"]
        
        # 获取用户
        get_response = await async_client.get(f"/user/{user_id}")
        assert get_response.status_code == 200
        
        user_data = get_response.json()
        assert user_data["username"] == "async_user"
```

## 测试数据管理

### 1. 测试数据工厂

```python
# tests/factories/user_factory.py
import factory
from factory.fuzzy import FuzzyText, FuzzyEmail
from module_admin.entity.do.user_do import UserDO

class UserFactory(factory.Factory):
    """用户测试数据工厂"""
    
    class Meta:
        model = UserDO
    
    id = factory.Sequence(lambda n: n + 1)
    username = FuzzyText(length=8, prefix="user_")
    email = FuzzyEmail()
    password = factory.LazyFunction(lambda: "password123")
    status = "0"
    create_time = factory.LazyFunction(datetime.now)
    update_time = factory.LazyFunction(datetime.now)

# 使用示例
def test_with_factory_data():
    """使用工厂数据测试"""
    # 创建单个用户
    user = UserFactory()
    assert user.username.startswith("user_")
    
    # 创建多个用户
    users = UserFactory.create_batch(5)
    assert len(users) == 5
    
    # 创建特定数据的用户
    custom_user = UserFactory(username="custom_user", email="custom@example.com")
    assert custom_user.username == "custom_user"
```

### 2. 测试数据清理

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(autouse=True)
async def cleanup_database(session: AsyncSession):
    """自动清理数据库"""
    yield
    
    # 测试完成后清理数据
    try:
        # 删除测试数据
        await session.execute(text("DELETE FROM sys_user WHERE username LIKE 'test_%'"))
        await session.execute(text("DELETE FROM sys_role WHERE role_name LIKE 'test_%'"))
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"清理测试数据失败: {e}")

@pytest.fixture(scope="function")
async def clean_session(session: AsyncSession):
    """清理会话"""
    yield session
    
    # 回滚未提交的更改
    await session.rollback()
```

## 性能测试

### 1. 基础性能测试

```python
# tests/test_performance.py
import pytest
import time
import asyncio
from module_admin.service.user_service import UserService

class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.slow
    def test_user_creation_performance(self):
        """测试用户创建性能"""
        user_service = UserService()
        
        start_time = time.time()
        
        # 批量创建用户
        for i in range(100):
            user_data = {
                "username": f"perf_user_{i}",
                "email": f"perf_{i}@example.com",
                "password": "password123"
            }
            user_service.create_user(user_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能断言
        assert execution_time < 5.0  # 100个用户创建应在5秒内完成
        print(f"创建100个用户耗时: {execution_time:.2f}秒")
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_user_query_performance(self, user_service):
        """测试用户查询性能"""
        # 准备测试数据
        users = []
        for i in range(1000):
            user_data = {
                "username": f"query_user_{i}",
                "email": f"query_{i}@example.com",
                "password": "password123"
            }
            user = await user_service.create_user(user_data)
            users.append(user)
        
        # 测试查询性能
        start_time = time.time()
        
        # 执行查询
        for i in range(100):
            user = await user_service.get_user_by_id(users[i].id)
            assert user is not None
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 性能断言
        assert execution_time < 2.0  # 100次查询应在2秒内完成
        print(f"100次查询耗时: {execution_time:.2f}秒")
```

### 2. 压力测试

```python
# tests/test_stress.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestStress:
    """压力测试类"""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, user_service):
        """测试并发用户创建"""
        async def create_user(user_id):
            """创建单个用户"""
            user_data = {
                "username": f"stress_user_{user_id}",
                "email": f"stress_{user_id}@example.com",
                "password": "password123"
            }
            return await user_service.create_user(user_data)
        
        # 并发创建100个用户
        start_time = time.time()
        
        tasks = [create_user(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证结果
        assert len(results) == 100
        assert execution_time < 10.0  # 并发创建应在10秒内完成
        
        print(f"并发创建100个用户耗时: {execution_time:.2f}秒")
    
    @pytest.mark.slow
    def test_thread_pool_performance(self, user_service):
        """测试线程池性能"""
        def create_user_sync(user_id):
            """同步创建用户"""
            user_data = {
                "username": f"thread_user_{user_id}",
                "email": f"thread_{user_id}@example.com",
                "password": "password123"
            }
            # 这里需要同步调用
            return user_service.create_user_sync(user_data)
        
        start_time = time.time()
        
        # 使用线程池
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_user_sync, i) for i in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证结果
        assert len(results) == 100
        assert execution_time < 15.0  # 线程池创建应在15秒内完成
        
        print(f"线程池创建100个用户耗时: {execution_time:.2f}秒")
```

## 测试覆盖率

### 1. 覆盖率配置

```python
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__init__.py
    */settings.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

### 2. 覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term-missing

# 生成XML格式报告（用于CI/CD）
pytest --cov=app --cov-report=xml

# 检查覆盖率阈值
pytest --cov=app --cov-fail-under=80
```

## 持续集成测试

### 1. GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:7.0
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        DATABASE_URL: mysql+asyncmy://root:root@localhost:3306/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest --cov=app --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### 2. 测试命令

```bash
# 运行所有测试
pytest

# 运行特定类型的测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m api           # 只运行API测试

# 运行特定测试文件
pytest tests/test_user_service.py

# 运行特定测试方法
pytest tests/test_user_service.py::TestUserService::test_get_user_by_id_success

# 运行失败的测试
pytest --lf

# 运行上次失败的测试
pytest --ff

# 并行运行测试
pytest -n auto

# 生成测试报告
pytest --html=report.html --self-contained-html
```

## 最佳实践

### 1. 测试设计原则
- **AAA模式**: Arrange（准备）、Act（执行）、Assert（断言）
- **单一职责**: 每个测试只测试一个功能点
- **独立性**: 测试之间相互独立，不依赖执行顺序
- **可读性**: 测试代码清晰易懂，便于维护

### 2. 测试数据管理
- **工厂模式**: 使用工厂创建测试数据
- **数据清理**: 测试完成后自动清理测试数据
- **隔离性**: 每个测试使用独立的测试数据
- **可重复性**: 测试可以重复执行且结果一致

### 3. 性能测试原则
- **基准测试**: 建立性能基准，监控性能变化
- **渐进测试**: 从小规模开始，逐步增加负载
- **资源监控**: 监控CPU、内存、数据库连接等资源使用
- **阈值设置**: 设置合理的性能阈值，及时发现问题

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 