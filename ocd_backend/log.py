import logging
import logging.config

from ocd_backend.settings import LOGGING

logging.config.dictConfig(LOGGING)


def get_source_logger(name=None):
    logger = logging.getLogger('ocd_backend')

    if name:
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(source)s] [%(module)s] [%(levelname)s] - %(message)s')
        logger.handlers[0].setFormatter(formatter)
        logger = logging.LoggerAdapter(logger, {'source': name})

    return logger
