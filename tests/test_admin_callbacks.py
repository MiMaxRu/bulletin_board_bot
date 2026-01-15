import pytest
import types
from app.bots import admin_bot


class DummyMessage:
    def __init__(self):
        self.edited = False
        self.replies = []

    async def edit_reply_markup(self, *args, **kwargs):
        self.edited = True

    async def reply(self, text, *args, **kwargs):
        self.replies.append(text)


class DummyQuery:
    def __init__(self, data):
        self.data = data
        self.message = DummyMessage()
        self.from_user = type("U", (), {"id": 1})()

    async def answer(self, *args, **kwargs):
        return None


@pytest.mark.asyncio
async def test_cb_approve_calls_approve(monkeypatch):
    called = {}

    async def fake_approve(session, ad_id):
        called['ad_id'] = ad_id
        return None

    monkeypatch.setattr(admin_bot, "approve_ad", fake_approve)

    q = DummyQuery("approve:42")
    await admin_bot.cb_approve(q)
    assert called.get('ad_id') == 42
    assert q.message.edited


@pytest.mark.asyncio
async def test_cb_reject_sets_pending_and_requests_comment(monkeypatch):
    q = DummyQuery("reject:7")
    # After calling cb_reject the message should prompt for comment; function uses reply()
    # We only ensure it does not raise and pending_rejects is set
    prev = dict(admin_bot.pending_rejects)
    await admin_bot.cb_reject(q)
    # verify pending_rejects set
    assert 1 in admin_bot.pending_rejects
    assert admin_bot.pending_rejects[1] == 7
    assert q.message.replies, "Expected a reply asking for rejection comment"
    # cleanup
    admin_bot.pending_rejects.clear()
