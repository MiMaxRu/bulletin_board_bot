from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.core.config import load_settings
from app.db.session import async_session
from app.db.repository import get_pending_ads
from app.services.moderation import approve_ad, reject_ad
from loguru import logger

settings = load_settings()

# lazy-safe bot creation (avoid token validation errors in tests)
if settings.telegram_token_admin:
    bot = Bot(token=settings.telegram_token_admin)
else:
    class _DummyBot:
        async def send_message(self, *args, **kwargs):
            return None
    bot = _DummyBot()

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


# simple in-memory map admin_id -> pending reject ad id (for comment flow)
pending_rejects: dict[int, int] = {}


@dp.callback_query(lambda c: c.data and c.data.startswith("reject:"))
async def cb_reject(query: types.CallbackQuery):
    ad_id = int(query.data.split(":", 1)[1])
    admin_id = query.from_user.id
    pending_rejects[admin_id] = ad_id
    await query.answer()
    await query.message.edit_reply_markup(None)
    await query.message.reply(f"Send rejection comment for ad #{ad_id}, or send '-' to reject without comment.")


@dp.message()
async def admin_text_handler(message: types.Message):
    admin_id = message.from_user.id
    if admin_id in pending_rejects:
        ad_id = pending_rejects.pop(admin_id)
        comment = None if message.text.strip() == "-" else message.text.strip()
        async with async_session() as session:
            await reject_ad(session, ad_id, comment)
        await message.answer(f"Ad #{ad_id} rejected.")
        return

    # ban/unban commands
    if message.text.startswith("/ban"):
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /ban <user_id>")
            return
        target = int(parts[1])
        async with async_session() as session:
            from app.services.users import ban_user
            u = await ban_user(session, target)
        await message.answer(f"User {target} banned.")
        return

    if message.text.startswith("/unban"):
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /unban <user_id>")
            return
        target = int(parts[1])
        async with async_session() as session:
            from app.services.users import unban_user
            u = await unban_user(session, target)
        await message.answer(f"User {target} unbanned.")
        return

async def start_polling():
    logger.info("Admin bot starting polling...")
    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Admin bot polling stopped unexpectedly")
        raise

if __name__ == "__main__":
    asyncio.run(start_polling())
