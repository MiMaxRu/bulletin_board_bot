from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from app.core.config import load_settings
from app.db.session import async_session
from app.services.users import ensure_user
from app.services.ads import create_ad_for_user
from loguru import logger

settings = load_settings()

# lazy-safe bot creation (avoid token validation errors in tests)
if settings.telegram_token_client:
    bot = Bot(token=settings.telegram_token_client)
else:
    class _DummyBot:
        async def send_message(self, *args, **kwargs):
            return None
    bot = _DummyBot()

dp = Dispatcher()


class AdStates(StatesGroup):
    title = State()
    description = State()
    phone = State()
    email = State()
    link = State()
    confirm = State()


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Hello! This is the client bot. Use /register to register and /create to publish an ad.")


@dp.message(Command(commands=["register"]))
async def cmd_register(message: types.Message):
    async with async_session() as session:
        user = await ensure_user(session, message.from_user.id)
    await message.answer("You are registered.")


@dp.message(Command(commands=["create"]))
async def cmd_create(message: types.Message, state: FSMContext):
    await state.set_state(AdStates.title)
    await message.answer("Enter title (required):")


@dp.message()
async def enter_title(message: types.Message, state: FSMContext):
    # quick pay confirm command handler inside client bot
    if message.text.startswith("/pay_confirm"):
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Usage: /pay_confirm <ad_id>")
            return
        ad_id = int(parts[1])
        from app.services.payments import verify_and_mark
        ok = await verify_and_mark(ad_id)
        if ok:
            await message.answer("Payment confirmed, ad sent for moderation.")
        else:
            await message.answer("Payment not found or verification failed.")
        return
    state_name = await state.get_state()
    if state_name == AdStates.title:
        await state.update_data(title=message.text)
        await state.set_state(AdStates.description)
        await message.answer("Enter description (required):")

    elif state_name == AdStates.description:
        await state.update_data(description=message.text)
        await state.set_state(AdStates.phone)
        await message.answer("Enter phone (optional, send - to skip):")

    elif state_name == AdStates.phone:
        if message.text.strip() != "-":
            await state.update_data(phone=message.text.strip())
        await state.set_state(AdStates.email)
        await message.answer("Enter email (optional, send - to skip):")

    elif state_name == AdStates.email:
        if message.text.strip() != "-":
            await state.update_data(email=message.text.strip())
        await state.set_state(AdStates.link)
        await message.answer("Enter link (optional, send - to skip):")

    elif state_name == AdStates.link:
        if message.text.strip() != "-":
            await state.update_data(link=message.text.strip())
        data = await state.get_data()
        text = f"Title: {data.get('title')}\nDescription: {data.get('description')}\nPhone: {data.get('phone', '')}\nEmail: {data.get('email', '')}\nLink: {data.get('link', '')}\n\nConfirm? (yes/no)"
        await state.set_state(AdStates.confirm)
        await message.answer(text)

    elif state_name == AdStates.confirm:
        if message.text.lower() in ("yes", "y"):
            data = await state.get_data()
            async with async_session() as session:
                user = await ensure_user(session, message.from_user.id)
                ad = await create_ad_for_user(
                    session,
                    title=data["title"],
                    description=data["description"],
                    author_id=user.id,
                    phone=data.get("phone"),
                    email=data.get("email"),
                    link=data.get("link"),
                )
                # monetization flow
                from app.core.config import load_settings
                s = load_settings()
                if s.monetization_enabled and int(s.price_per_post) > 0:
                    from app.services.payments import create_payment_for_ad, get_provider
                    price = int(s.price_per_post)
                    pid = await create_payment_for_ad(session, ad.id, price=price)
                    # send payment instructions (mock)
                    provider = get_provider()
                    await message.answer(f"Payment required: {price}. Payment id: {pid}. After payment run /pay_confirm {ad.id}")
                else:
                    # notify admins about new ad
                    from app.services.moderation import notify_admins
                    await notify_admins(session, ad)
                    await message.answer("Ad submitted for moderation.")
            await state.clear()
        else:
            await message.answer("Cancelled.")
            await state.clear()

async def start_polling():
    logger.info("Client bot starting polling...")
    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Client bot polling stopped unexpectedly")
        raise

if __name__ == "__main__":
    asyncio.run(start_polling())
