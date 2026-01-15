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

settings = load_settings()

bot = Bot(token=settings.telegram_token_client)
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
            await message.answer("Ad submitted for moderation.")
            await state.clear()
        else:
            await message.answer("Cancelled.")
            await state.clear()

async def start_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_polling())
