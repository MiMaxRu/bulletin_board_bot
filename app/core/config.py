from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # loads .env.* files if present

@dataclass
class Settings:
    telegram_token_client: str
    telegram_token_admin: str
    database_url: str
    use_webhook: bool = False
    env: str = "development"


def load_settings() -> Settings:
    return Settings(
        telegram_token_client=os.getenv("TELEGRAM_TOKEN_CLIENT", ""),
        telegram_token_admin=os.getenv("TELEGRAM_TOKEN_ADMIN", ""),
        database_url=os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/bulletin"),
        use_webhook=os.getenv("USE_WEBHOOK", "false").lower() in ("1", "true", "yes"),
        env=os.getenv("ENV", "development"),
    )
