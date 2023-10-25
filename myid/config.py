from typing import Union

from pydantic import BaseSettings


class MyIdSettings(BaseSettings):
    MYIDSDK_PROJECT_NAME: str = "myid-sdk"
    MYIDSDK_TX_RETRY_COUNT: int = 5
    MYIDSDK_TX_SLEEP_TIME: Union[int, float] = 1
    MYIDSDK_LOG_ENABLE_LOGGER: bool = False

    class Config:
        case_sensitive = True


settings = MyIdSettings()
