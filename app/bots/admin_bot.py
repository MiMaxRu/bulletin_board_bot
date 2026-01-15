from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.core.config import load_settings
from app.db.session import async_session
from app.db.repository import get_pending_ads
from app.services.moderation import approve_ad, reject_ad

settings = load_settings()

bot = Bot(token=settings.telegram_token_admin)
dp = Dispatcher()


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Hello! This is the admin bot.")


@dp.message(Command(commands=["pending"]))
async def cmd_pending(message: types.Message):
    async with async_session() as session:
        ads = await get_pending_ads(session)
    if not ads:
        await message.answer("No pending ads")
        return
    for ad in ads:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Approve", callback_data=f"approve:{ad.id}"),
            InlineKeyboardButton(text="Reject", callback_data=f"reject:{ad.id}"),
        ]])
        text = f"#{ad.id}\nTitle: {ad.title}\n{ad.description}"
        await message.answer(text=text, reply_markup=kb)


@dp.callback_query(lambda c: c.data and c.data.startswith("approve:"))
async def cb_approve(query: types.CallbackQuery):
    ad_id = int(query.data.split(":", 1)[1])
    async with async_session() as session:
        await approve_ad(session, ad_id)
    await query.answer("Approved")
    await query.message.edit_reply_markup(None)


@dp.callback_query(lambda c: c.data and c.data.startswith("reject:"))
async def cb_reject(query: types.CallbackQuery):
    ad_id = int(query.data.split(":", 1)[1])
    # simple rejection without comment for now
    async with async_session() as session:
        await reject_ad(session, ad_id)
    await query.answer("Rejected")
    await query.message.edit_reply_markup(None)

async def start_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_polling())
