from loguru import logger


def configure_logging() -> None:
    logger.add("-", level="INFO")
