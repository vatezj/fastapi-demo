from config.database import async_engine, AsyncSessionLocal, Base
from utils.log_util import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncSession:
    """
    数据库会话依赖函数
    
    为FastAPI提供数据库会话依赖，优化异步上下文管理
    """
    session = AsyncSessionLocal()
    try:
        # 确保会话在正确的异步上下文中
        yield session
    except Exception as e:
        # 记录错误并回滚
        logger.error(f"数据库会话异常: {str(e)}")
        try:
            await session.rollback()
        except Exception as rollback_error:
            logger.error(f"回滚失败: {str(rollback_error)}")
        raise
    finally:
        try:
            await session.close()
        except Exception as close_error:
            logger.error(f"关闭会话失败: {str(close_error)}")


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
