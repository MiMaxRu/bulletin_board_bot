from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import create_ad


async def create_ad_for_user(session: AsyncSession, title: str, description: str, author_id: int, phone: Optional[str] = None, email: Optional[str] = None, link: Optional[str] = None):
    ad = await create_ad(session, title=title, description=description, author_id=author_id, phone=phone, email=email, link=link)
    return ad
