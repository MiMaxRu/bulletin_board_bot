from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher, types
from app.core.config import load_settings

settings = load_settings()

bot = Bot(token=settings.telegram_token_admin)
dp = Dispatcher()

@dp.message("/start")
async def cmd_start(message: types.Message):
    await message.answer("Hello! This is the admin bot (skeleton).")

async def start_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_polling())
