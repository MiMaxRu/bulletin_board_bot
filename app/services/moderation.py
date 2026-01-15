from __future__ import annotations

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import get_admins, get_user_by_id, set_ad_status, get_ad_by_id
from app.db.models import Ad


async def notify_admins(session: AsyncSession, ad: Ad) -> None:
    # import admin bot lazily to avoid circular import on module load
    from app.bots import admin_bot

    admins = await get_admins(session)
    text = f"New ad #{ad.id} pending moderation:\nTitle: {ad.title}\n{ad.description}\n\nUse /pending to manage."
    for a in admins:
        try:
            await admin_bot.bot.send_message(chat_id=a.tg_id, text=text)
        except Exception:
            # best-effort notify
            pass


async def approve_ad(session: AsyncSession, ad_id: int) -> Ad:
    ad = await set_ad_status(session, ad_id, "approved")
    # notify author
    author = await get_user_by_id(session, ad.author_id)
    try:
        from app.bots import client_bot
        await client_bot.bot.send_message(chat_id=author.tg_id, text=f"Your ad #{ad.id} was approved")
    except Exception:
        pass
    return ad


async def reject_ad(session: AsyncSession, ad_id: int, comment: str | None = None) -> Ad:
    ad = await set_ad_status(session, ad_id, "rejected")
    author = await get_user_by_id(session, ad.author_id)
    try:
        from app.bots import client_bot
        await client_bot.bot.send_message(chat_id=author.tg_id, text=f"Your ad #{ad.id} was rejected. {comment or ''}")
    except Exception:
        pass
    return ad
