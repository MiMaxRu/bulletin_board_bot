from __future__ import annotations

import asyncio
from app.core.logging import setup_logging
from app.bots import client_bot, admin_bot

setup_logging()

async def main():
    # start both bots in same event loop
    await asyncio.gather(client_bot.start_polling(), admin_bot.start_polling())

if __name__ == "__main__":
    asyncio.run(main())
