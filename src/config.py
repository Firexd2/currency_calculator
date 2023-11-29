from pathlib import Path

from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).resolve()
ROOT_PATH = BASE_PATH.parent


class Settings(BaseSettings):
    POSTGRES_URI: str

    class Config:
        env_file = ROOT_PATH / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
