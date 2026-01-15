import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, create_ad, get_ad_by_id
from app.services.payments import get_provider, create_payment_for_ad, verify_and_mark

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_mock_payment_flow(monkeypatch):
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        user = await create_user(session, tg_id=10)
        ad = await create_ad(session, title="t", description="d", author_id=user.id)

        provider = get_provider()
        pid = await create_payment_for_ad(session, ad.id, price=100)
        assert pid.startswith("mock_")

        # mock provider internal store to mark payment as done
        # provider is MockProvider with internal store
        provider._store[pid] = True

        ok = await verify_and_mark(ad.id, session=session)
        assert ok
        ad2 = await get_ad_by_id(session, ad.id)
        assert ad2.is_paid
        assert ad2.status == "pending"
