from loguru import logger

def setup_logging():
    logger.remove()
    logger.add("/dev/stdout", level="INFO")
