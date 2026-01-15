import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, get_user_by_tg, create_ad


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_create_user_and_get():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        u = await create_user(session, tg_id=12345)
        assert u.tg_id == 12345

        fetched = await get_user_by_tg(session, 12345)
        assert fetched.id == u.id


@pytest.mark.asyncio
async def test_create_ad():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        u = await create_user(session, tg_id=54321)
        ad = await create_ad(session, title="t", description="d", author_id=u.id)
        assert ad.status == "pending"
        assert ad.title == "t"
