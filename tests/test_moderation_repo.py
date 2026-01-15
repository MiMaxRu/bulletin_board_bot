import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, create_ad, get_pending_ads, set_ad_status

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_pending_and_status_changes():
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        u = await create_user(session, tg_id=1)
        ad = await create_ad(session, title="t", description="d", author_id=u.id)
        pendings = await get_pending_ads(session)
        assert any(a.id == ad.id for a in pendings)

        await set_ad_status(session, ad.id, "approved")
        pendings_after = await get_pending_ads(session)
        assert all(a.id != ad.id for a in pendings_after)
