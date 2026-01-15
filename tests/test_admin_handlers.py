import pytest
import types
from app.bots import admin_bot


class DummyMessage:
    def __init__(self):
        self.answers = []

    async def answer(self, *args, **kwargs):
        self.answers.append((args, kwargs))


@pytest.mark.asyncio
async def test_cmd_pending_calls_answer(monkeypatch):
    # prepare a fake pending ad
    ad = types.SimpleNamespace(id=1, title="T", description="D")

    async def fake_get_pending_ads(session):
        return [ad]

    monkeypatch.setattr(admin_bot, "get_pending_ads", fake_get_pending_ads)

    msg = DummyMessage()
    await admin_bot.cmd_pending(msg)
    assert msg.answers, "Expected at least one answer"
    args, kwargs = msg.answers[0]
    text = args[0] if args else kwargs.get('text')
    assert text is not None
    assert "Title: T" in text
