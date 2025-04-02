import typing as t
from functools import lru_cache

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGO_URI: str


settings = Settings()


@lru_cache()
def create_settings() -> Settings:
    return settings


SettingsDep = t.Annotated[Settings, Depends(create_settings)]
