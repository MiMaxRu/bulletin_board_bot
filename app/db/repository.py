from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Ad


async def get_user_by_tg(session: AsyncSession, tg_id: int) -> Optional[User]:
    q = await session.execute(select(User).where(User.tg_id == tg_id))
    return q.scalars().first()


async def create_user(session: AsyncSession, tg_id: int, is_admin: bool = False) -> User:
    user = User(tg_id=tg_id, is_admin=is_admin)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_ad(session: AsyncSession, title: str, description: str, author_id: int, phone: Optional[str] = None, email: Optional[str] = None, link: Optional[str] = None) -> Ad:
    ad = Ad(title=title, description=description, author_id=author_id, status="pending", phone=phone, email=email, link=link)
    session.add(ad)
    await session.commit()
    await session.refresh(ad)
    return ad
