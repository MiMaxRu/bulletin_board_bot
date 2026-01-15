import pytest
from app.services.payments import YooKassaProvider


@pytest.mark.asyncio
async def test_yookassa_provider_sandbox_flow():
    p = YooKassaProvider(sandbox=True)
    pid = await p.create_payment(100, "test")
    assert pid.startswith("yoo_")
    # mark paid in internal store
    p._store[pid] = True
    ok = await p.verify_payment(pid)
    assert ok
