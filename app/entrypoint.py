import argparse
import asyncio
import os

import uvicorn
from loguru import logger

from app.main import app


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dev", dest="dev", action="store_true")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    env = os.getenv("ENV", "development")
    logger.info("Starting Bulletin Board service (env={})", env)
    # Run FastAPI app with uvicorn for healthcheck and to keep container alive
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
