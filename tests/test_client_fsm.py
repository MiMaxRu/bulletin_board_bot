import pytest
from types import SimpleNamespace
from app.bots import client_bot
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repository import get_user_by_tg

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class FakeState:
    def __init__(self):
        self._state = None
        self._data = {}

    async def set_state(self, state):
        self._state = state

    async def get_state(self):
        return self._state

    async def update_data(self, **kwargs):
        self._data.update(kwargs)

    async def get_data(self):
        return self._data

    async def clear(self):
        self._state = None
        self._data = {}


class FakeMessage:
    def __init__(self, text, user_id=1):
        self.text = text
        self.from_user = SimpleNamespace(id=user_id)
        self.answers = []

    async def answer(self, *args, **kwargs):
        self.answers.append((args, kwargs))


@pytest.mark.asyncio
async def test_create_flow_without_payment(monkeypatch):
    # setup in-memory DB
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # ensure settings -> monetization disabled
    monkeypatch.setattr(client_bot, "settings", SimpleNamespace(monetization_enabled=False, price_per_post=0))

    # monkeypatch async_session used in client_bot
    monkeypatch.setattr(client_bot, "async_session", async_session)

    # monkeypatch notify_admins to record calls
    called = {}

    async def fake_notify(session, ad):
        called['ad_id'] = ad.id

    monkeypatch.setattr('app.services.moderation.notify_admins', fake_notify, raising=False)

    state = FakeState()

    # simulate commands
    msg = FakeMessage("/create")
    await client_bot.cmd_create(msg, state)

    # title
    m1 = FakeMessage("My title")
    await client_bot.enter_title(m1, state)
    # description
    m2 = FakeMessage("My desc")
    await client_bot.enter_title(m2, state)
    # phone
    m3 = FakeMessage("-")
    await client_bot.enter_title(m3, state)
    # email
    m4 = FakeMessage("-")
    await client_bot.enter_title(m4, state)
    # link
    m5 = FakeMessage("-")
    await client_bot.enter_title(m5, state)
    # confirm yes
    m6 = FakeMessage("yes")
    # attach a session to message's from_user id via DB existing or creation
    # call through
    await client_bot.enter_title(m6, state)

    # check ad was submitted for moderation (notify called)
    assert 'ad_id' in called


@pytest.mark.asyncio
async def test_create_flow_with_payment(monkeypatch):
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # monkeypatch load_settings used inside handler (patch the core module function)
    import app.core.config as config_mod
    monkeypatch.setattr(config_mod, 'load_settings', lambda: SimpleNamespace(monetization_enabled=True, price_per_post=10, payment_provider='mock'))
    monkeypatch.setattr(client_bot, "async_session", async_session)

    # monkeypatch create_payment_for_ad (set on module directly to be safe)
    called = {}

    async def fake_create_payment(session, ad_id, price):
        called['ad_id'] = ad_id
        called['price'] = price
        return "pid123"

    import app.services.payments as payments_mod
    monkeypatch.setattr(payments_mod, 'create_payment_for_ad', fake_create_payment)

    # patched core.load_settings will be used by client_bot when imported inside handler
    pass

    # sanity check ensure_user works with provided sessionmaker
    from app.services.users import ensure_user
    async with async_session() as session:
        u = await ensure_user(session, 3)
        assert u.tg_id == 3

    state = FakeState()
    msg = FakeMessage("/create", user_id=3)
    await client_bot.cmd_create(msg, state)

    await client_bot.enter_title(FakeMessage("Title"), state)
    s = await state.get_state()
    assert s == client_bot.AdStates.description
    await client_bot.enter_title(FakeMessage("Desc"), state)
    s = await state.get_state()
    assert s == client_bot.AdStates.phone
    await client_bot.enter_title(FakeMessage("-"), state)
    s = await state.get_state()
    assert s == client_bot.AdStates.email
    await client_bot.enter_title(FakeMessage("-"), state)
    s = await state.get_state()
    assert s == client_bot.AdStates.link
    await client_bot.enter_title(FakeMessage("-"), state)
    s = await state.get_state()
    assert s == client_bot.AdStates.confirm
    await client_bot.enter_title(FakeMessage("yes"), state)
    s = await state.get_state()
    assert s is None

    # check DB ad status
    async with async_session() as session:
        from app.db.repository import get_user_by_tg, get_pending_ads, get_ad_by_id
        u = await get_user_by_tg(session, 3)
        # fetch any ads for user
        pendings = await get_pending_ads(session)
        # find ad for this user
        ad_for_user = None
        for a in pendings:
            if a.author_id == u.id:
                ad_for_user = a
                break
    # in monetization enabled case ad should be awaiting_payment (not pending) before payment
    assert ad_for_user is None, "Ad should not be in pending since payment expected"
    # payment creation should have been triggered
    assert 'ad_id' in called and called['price'] == 10
