from __future__ import annotations

from typing import Protocol, runtime_checkable
from app.core.config import load_settings
from app.db.repository import set_ad_payment, mark_ad_paid, get_ad_by_id
from app.db.session import async_session

settings = load_settings()


@runtime_checkable
class PaymentProvider(Protocol):
    async def create_payment(self, amount: int, description: str) -> str:
        """Return payment_id or url"""

    async def verify_payment(self, payment_id: str) -> bool:
        """Verify payment status (sandbox or real)"""


class MockProvider:
    def __init__(self):
        self._store: dict[str, bool] = {}

    async def create_payment(self, amount: int, description: str) -> str:
        pid = f"mock_{len(self._store) + 1}"
        self._store[pid] = False
        return pid

    async def verify_payment(self, payment_id: str) -> bool:
        # for tests we flip to True when verifying
        return self._store.get(payment_id, False)


_provider: PaymentProvider | None = None


def get_provider() -> PaymentProvider:
    global _provider
    if _provider is None:
        if settings.payment_provider == "mock":
            _provider = MockProvider()
        else:
            _provider = MockProvider()  # default fallback
    return _provider


async def create_payment_for_ad(session, ad_id: int, price: int) -> str:
    provider = get_provider()
    ad = await get_ad_by_id(session, ad_id)
    pid = await provider.create_payment(price, f"Payment for ad #{ad.id}")
    await set_ad_payment(session, ad_id, price=price, payment_id=pid)
    return pid


async def verify_and_mark(ad_id: int, session=None) -> bool:
    # accept optional session for tests; otherwise create own
    own = False
    if session is None:
        own = True
        session = async_session()

    if own:
        async with session as s:
            ad = await get_ad_by_id(s, ad_id)
            if not ad or not ad.payment_id:
                return False
            provider = get_provider()
            paid = await provider.verify_payment(ad.payment_id)
            if paid:
                await mark_ad_paid(s, ad_id)
                # notify admins
                from app.services.moderation import notify_admins
                await notify_admins(s, ad)
            return paid
    else:
        ad = await get_ad_by_id(session, ad_id)
        if not ad or not ad.payment_id:
            return False
        provider = get_provider()
        paid = await provider.verify_payment(ad.payment_id)
        if paid:
            await mark_ad_paid(session, ad_id)
            from app.services.moderation import notify_admins
            await notify_admins(session, ad)
        return paid
