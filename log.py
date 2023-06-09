import os
import logging


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    log_level = os.getenv('LOG_LEVEL', 'INFO')
    if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.INFO)

    return logger


log = setup_logger()
