from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import get_user_by_tg, create_user, set_user_banned


async def ensure_user(session: AsyncSession, tg_id: int, is_admin: bool = False):
    u = await get_user_by_tg(session, tg_id)
    if u:
        return u
    return await create_user(session, tg_id, is_admin=is_admin)


async def ban_user(session: AsyncSession, user_id: int):
    return await set_user_banned(session, user_id, True)


async def unban_user(session: AsyncSession, user_id: int):
    return await set_user_banned(session, user_id, False)
