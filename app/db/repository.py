from __future__ import annotations

from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Ad


async def get_user_by_tg(session: AsyncSession, tg_id: int) -> Optional[User]:
    q = await session.execute(select(User).where(User.tg_id == tg_id))
    return q.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    q = await session.execute(select(User).where(User.id == user_id))
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


async def get_ad_by_id(session: AsyncSession, ad_id: int) -> Optional[Ad]:
    q = await session.execute(select(Ad).where(Ad.id == ad_id))
    return q.scalars().first()


async def get_pending_ads(session: AsyncSession) -> List[Ad]:
    q = await session.execute(select(Ad).where(Ad.status == "pending"))
    return q.scalars().all()


async def set_ad_status(session: AsyncSession, ad_id: int, status: str) -> Optional[Ad]:
    await session.execute(update(Ad).where(Ad.id == ad_id).values(status=status))
    await session.commit()
    return await get_ad_by_id(session, ad_id)


async def set_ad_payment(session: AsyncSession, ad_id: int, price: int, payment_id: str) -> Optional[Ad]:
    await session.execute(update(Ad).where(Ad.id == ad_id).values(price=price, payment_id=payment_id, status="awaiting_payment"))
    await session.commit()
    return await get_ad_by_id(session, ad_id)


async def mark_ad_paid(session: AsyncSession, ad_id: int) -> Optional[Ad]:
    await session.execute(update(Ad).where(Ad.id == ad_id).values(is_paid=True, status="pending"))
    await session.commit()
    return await get_ad_by_id(session, ad_id)


async def get_admins(session: AsyncSession) -> List[User]:
    q = await session.execute(select(User).where(User.is_admin == True))
    return q.scalars().all()


async def set_user_banned(session: AsyncSession, user_id: int, banned: bool) -> Optional[User]:
    await session.execute(update(User).where(User.id == user_id).values(is_banned=banned))
    await session.commit()
    return await get_user_by_id(session, user_id)
