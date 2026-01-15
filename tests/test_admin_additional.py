import pytest
from app.bots import admin_bot


class DummyMessage:
    def __init__(self, text="", user_id=1):
        self.text = text
        self.answers = []
        self.from_user = type('U', (), {'id': user_id})()

    async def answer(self, *args, **kwargs):
        self.answers.append((args, kwargs))


@pytest.mark.asyncio
async def test_cmd_pending_no_ads(monkeypatch):
    async def fake_get_pending_ads(session):
        return []

    monkeypatch.setattr(admin_bot, "get_pending_ads", fake_get_pending_ads)
    msg = DummyMessage()
    await admin_bot.cmd_pending(msg)
    assert msg.answers
    text = msg.answers[0][1].get('text') or (msg.answers[0][0][0] if msg.answers[0][0] else '')
    assert "No pending ads" in text


@pytest.mark.asyncio
async def test_ban_unban_commands(monkeypatch):
    # test ban command
    called = {}

    async def fake_ban(session, user_id):
        called['ban'] = user_id
        return None

    monkeypatch.setattr('app.services.users.ban_user', fake_ban, raising=False)

    msg = DummyMessage("/ban 123")
    await admin_bot.admin_text_handler(msg)
    assert called.get('ban') == 123

    async def fake_unban(session, user_id):
        called['unban'] = user_id
        return None

    monkeypatch.setattr('app.services.users.unban_user', fake_unban, raising=False)
    msg2 = DummyMessage("/unban 123")
    await admin_bot.admin_text_handler(msg2)
    assert called.get('unban') == 123
