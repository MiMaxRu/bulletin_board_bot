import pytest
from app.bots import client_bot


class DummyMessage:
    def __init__(self, text):
        self.text = text
        self.answers = []
        self.from_user = type("U", (), {"id": 1})()

    async def answer(self, *args, **kwargs):
        self.answers.append((args, kwargs))


@pytest.mark.asyncio
async def test_pay_confirm_success(monkeypatch):
    async def fake_verify(ad_id, session=None):
        return True

    monkeypatch.setattr('app.services.payments.verify_and_mark', fake_verify, raising=False)
    msg = DummyMessage("/pay_confirm 5")
    state = object()  # unused
    await client_bot.enter_title(msg, state)
    assert any("Payment confirmed" in (a[0][0] if a[0] else a[1].get('text', '')) for a in msg.answers)


@pytest.mark.asyncio
async def test_pay_confirm_fail(monkeypatch):
    async def fake_verify(ad_id, session=None):
        return False

    monkeypatch.setattr('app.services.payments.verify_and_mark', fake_verify, raising=False)
    msg = DummyMessage("/pay_confirm 5")
    state = object()
    await client_bot.enter_title(msg, state)
    assert any("Payment not found" in (a[0][0] if a[0] else a[1].get('text', '')) for a in msg.answers)
