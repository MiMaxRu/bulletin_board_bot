"""Service layer: users (scaffold)."""

from typing import Optional


class UserService:
    async def register(self, username: str, phone: Optional[str] = None) -> int:
        return 1
