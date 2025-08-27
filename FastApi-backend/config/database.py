from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from urllib.parse import quote_plus
from config.env import DataBaseConfig

ASYNC_SQLALCHEMY_DATABASE_URL = (
    f'mysql+aiomysql://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
    f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
)
if DataBaseConfig.db_type == 'postgresql':
    ASYNC_SQLALCHEMY_DATABASE_URL = (
        f'postgresql+asyncpg://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
        f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
    )

async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=DataBaseConfig.db_echo,
    max_overflow=DataBaseConfig.db_max_overflow,
    pool_size=DataBaseConfig.db_pool_size,
    pool_recycle=DataBaseConfig.db_pool_recycle,
    pool_timeout=DataBaseConfig.db_pool_timeout,
    # 优化异步配置，避免Greenlet错误
    pool_pre_ping=False,  # 禁用连接前ping测试
    future=True,  # 设置为True，符合新版本SQLAlchemy要求
    # 添加异步优化配置
    poolclass=None,  # 使用默认连接池
    # 确保异步上下文正确
    isolation_level="READ_COMMITTED",  # 设置事务隔离级别
    # 连接参数 - 简化配置，避免语法错误
    connect_args={
        "charset": "utf8mb4"
    }
)

# 创建会话工厂，使用优化的异步配置
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    # 添加异步优化配置
    expire_on_commit=False  # 避免提交后对象过期
)


class Base(AsyncAttrs, DeclarativeBase):
    pass
