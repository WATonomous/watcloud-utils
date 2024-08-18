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

    # set the logging level for some common noisy loggers
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
    
    # add nicer formatting to uvicorn logs
    uvicorn_logger = logging.getLogger("uvicorn")
    if uvicorn_logger.handlers:
        uvicorn_logger.handlers[0].setFormatter(formatter)
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    if uvicorn_access_logger.handlers:
        uvicorn_access_logger.handlers[0].setFormatter(formatter)
