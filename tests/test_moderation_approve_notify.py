import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import create_user, create_ad
from app.services import moderation

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class DummyBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


@pytest.mark.asyncio
async def test_approve_notifies_author(monkeypatch):
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        admin = await create_user(session, tg_id=10, is_admin=True)
        user = await create_user(session, tg_id=20)
        ad = await create_ad(session, title="t", description="d", author_id=user.id)

        dummy_client = DummyBot()
        import app.bots.client_bot as client_bot
        monkeypatch.setattr(client_bot, "bot", dummy_client)

        # call approve
        await moderation.approve_ad(session, ad.id)

        assert dummy_client.sent, "Author should be notified upon approval"
        assert dummy_client.sent[0][0] == user.tg_id
