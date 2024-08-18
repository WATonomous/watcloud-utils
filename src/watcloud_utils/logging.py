import logging
import os

logger = logging.getLogger()

def set_up_logging():
    logger.setLevel(os.environ.get("APP_LOG_LEVEL", "INFO"))
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
