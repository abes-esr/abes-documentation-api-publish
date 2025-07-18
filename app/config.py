import os
from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    DOCUMENTATION_API_PUBLISH_USER: str
    DOCUMENTATION_API_PUBLISH_PASSWORD: str
    DOCUMENTATION_API_PUBLISH_SKIN: str
    DOCUMENTATION_API_PUBLISH_ZIP_PATH: str
    DOCUMENTATION_API_PUBLISH_LOCAL_PATH: str
    DOCUMENTATION_API_PUBLISH_LOCAL_BACKUP_PATH: str
    DOCUMENTATION_API_PUBLISH_API_KEY: str

    class Config:
        env_file = ".env"

config = Config()
