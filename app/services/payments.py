"""Payments adapter scaffold.

План: реализовать абстракцию PaymentProvider и конкретные адаптеры для sandbox (mock) и реального провайдера.
"""

from typing import Protocol


class PaymentProvider(Protocol):
    async def create_payment(self, amount: float, **kwargs) -> dict:
        ...


class MockProvider:
    async def create_payment(self, amount: float, **kwargs) -> dict:
        return {"status": "ok", "amount": amount}
