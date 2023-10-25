from loguru import logger

from myid.config import settings

if settings.MYIDSDK_LOG_ENABLE_LOGGER:
    logger.enable(__name__)
else:
    logger.disable(__name__)

logger.debug(f"{settings.MYIDSDK_LOG_ENABLE_LOGGER=}")
logger.debug(f"{settings.__repr_name__()}: {settings.dict()}")
