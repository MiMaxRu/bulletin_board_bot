import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, get_user_by_tg, set_user_banned

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_ban_unban_user():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        u = await create_user(session, tg_id=555)
        assert not u.is_banned
        await set_user_banned(session, u.id, True)
        u2 = await get_user_by_tg(session, 555)
        assert u2.is_banned
        await set_user_banned(session, u.id, False)
        u3 = await get_user_by_tg(session, 555)
        assert not u3.is_banned
