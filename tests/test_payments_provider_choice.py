import pytest
from app.services import payments
import app.core.config as config_mod


@pytest.mark.asyncio
async def test_get_provider_yookassa(monkeypatch):
    monkeypatch.setattr(config_mod, 'load_settings', lambda: type('S', (), {'payment_provider': 'yookassa'})())
    # reload provider factory by resetting internal variable and update module settings
    payments._provider = None
    payments.settings = config_mod.load_settings()
    p = payments.get_provider()
    assert p.__class__.__name__ == 'YooKassaProvider'


@pytest.mark.asyncio
async def test_get_provider_mock_default(monkeypatch):
    monkeypatch.setattr(config_mod, 'load_settings', lambda: type('S', (), {'payment_provider': 'mock'})())
    payments._provider = None
    payments.settings = config_mod.load_settings()
    p = payments.get_provider()
    assert p.__class__.__name__ == 'MockProvider'
