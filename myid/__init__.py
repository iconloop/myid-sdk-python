from loguru import logger

from myid.config import settings

if settings.LOG_ENABLE_MYID_LOGGER:
    logger.enable(__name__)
else:
    logger.disable(__name__)

logger.debug(f"LOG_ENABLE_MYID_LOGGER is {settings.LOG_ENABLE_MYID_LOGGER}")
logger.debug(f"{settings.__repr_name__()}: {settings.dict()}")
