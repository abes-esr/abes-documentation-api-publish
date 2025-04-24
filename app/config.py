import os
from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    GENERATION_USER: str
    GENERATION_PASSWORD: str
    GENERATION_WORKSHOP: str
    GENERATION_GENERATOR: str
    GENERATION_SKIN: str
    GENERATION_ZIP_PATH: str
    DEPLOYMENT_LOCAL_PATH: str
    API_KEY: str

    class Config:
        env_file = ".env"

config = Config()
