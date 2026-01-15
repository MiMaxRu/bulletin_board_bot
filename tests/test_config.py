from app.core.config import load_settings


def test_load_settings():
    s = load_settings()
    assert hasattr(s, "telegram_token_client")
    assert hasattr(s, "telegram_token_admin")
    assert hasattr(s, "database_url")
