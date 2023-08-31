from loguru import logger
from pydantic import BaseSettings

PROJECT_NAME = "myid-sdk"

DEFAULT_LOG_LEVEL = "TRACE"
DEFAULT_LOG_FILE = "logs/myid_sdk.log"
DEFAULT_LOG_ROTATION = "daily"
DEFAULT_LOG_RETENTION = "1 months"
DEFAULT_LOG_COMPRESSION = "tar.gz"


class Settings(BaseSettings):
    PROJECT_NAME: str = PROJECT_NAME

    LOG_LEVEL: str = DEFAULT_LOG_LEVEL
    LOG_FILE: str = DEFAULT_LOG_FILE
    LOG_ROTATION: str = DEFAULT_LOG_ROTATION
    LOG_RETENTION: str = DEFAULT_LOG_RETENTION
    LOG_COMPRESSION: str = DEFAULT_LOG_COMPRESSION

    class Config:
        case_sensitive = True


settings = Settings()
logger.debug(f"{settings.PROJECT_NAME}: {settings.dict()}")
