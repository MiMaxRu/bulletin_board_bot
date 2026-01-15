from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    env: str = "development"
    bot_token_client: Optional[str] = None
    bot_token_admin: Optional[str] = None
    database_url: str = "sqlite+aiosqlite:///./test.db"
    use_webhook: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
