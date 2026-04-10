from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Engine and session are created lazily to avoid import-time side effects
_engine = None
_async_session = None


def get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        from src.config import get_settings
        _engine = create_async_engine(get_settings().database_url, echo=False)
    return _engine


def get_async_session():
    global _async_session
    if _async_session is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _async_session = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session


async def get_session():
    async with get_async_session()() as session:
        yield session
