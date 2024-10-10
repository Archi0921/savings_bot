from .models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import logging

logger = logging.getLogger(__name__)
DATABASE_URL = "sqlite+aiosqlite:///./database/bot.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        logger.info('Создали бд')
        await conn.run_sync(Base.metadata.create_all)
