"""Moderation service (scaffold)."""


class ModerationService:
    async def approve(self, ad_id: int, admin_id: int) -> bool:
        return True

    async def reject(self, ad_id: int, admin_id: int, comment: str = "") -> bool:
        return True
