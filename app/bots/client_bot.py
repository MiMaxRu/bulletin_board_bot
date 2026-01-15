"""Клиентский бот — scaffold (позже: aiogram handlers, FSM)."""

from typing import Any


async def start_client_bot(token: str | None = None) -> Any:
    # stub: реальная инициализация aiogram добавится на этапе 2
    if not token:
        return None
    return True
