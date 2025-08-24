from config.database import async_engine, AsyncSessionLocal, Base
from utils.log_util import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncSession:
    """
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
    
    使用更简单的会话管理方式，避免复杂的异常处理
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_create_table():
    """
    应用启动时初始化数据库连接
    """
    logger.info('初始化数据库连接...')
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info('数据库连接成功')
    except Exception as e:
        logger.error(f'数据库连接失败: {e}')
        raise
