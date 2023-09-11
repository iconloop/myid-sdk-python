from pydantic import BaseSettings


class MyIdSettings(BaseSettings):
    PROJECT_NAME: str = "myid-sdk"
    LOG_ENABLE_MYID_LOGGER: bool = False

    class Config:
        case_sensitive = True


settings = MyIdSettings()
