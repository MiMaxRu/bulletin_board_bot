import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, create_ad

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class DummyBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


@pytest.mark.asyncio
async def test_notify_admins(monkeypatch):
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        admin = await create_user(session, tg_id=999, is_admin=True)
        user = await create_user(session, tg_id=1)
        ad = await create_ad(session, title="t", description="d", author_id=user.id)

        dummy = DummyBot()
        # patch the admin bot
        import app.bots.admin_bot as admin_bot_module
        monkeypatch.setattr(admin_bot_module, "bot", dummy)

        from app.services.moderation import notify_admins
        await notify_admins(session, ad)

        assert dummy.sent, "Expected at least one admin notification"
        assert dummy.sent[0][0] == 999
        assert str(ad.id) in dummy.sent[0][1]


@pytest.mark.asyncio
async def test_approve_and_reject(monkeypatch):
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        author = await create_user(session, tg_id=3333)
        ad = await create_ad(session, title="tt", description="dd", author_id=author.id)

        dummy = DummyBot()
        import app.bots.client_bot as client_bot_module
        monkeypatch.setattr(client_bot_module, "bot", dummy)

        from app.services.moderation import approve_ad, reject_ad
        a = await approve_ad(session, ad.id)
        assert a.status == "approved"
        assert dummy.sent and dummy.sent[0][0] == author.tg_id

        dummy.sent.clear()
        r = await reject_ad(session, ad.id, comment="nope")
        assert r.status == "rejected"
        assert dummy.sent and dummy.sent[0][0] == author.tg_id
