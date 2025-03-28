import typing as t
import fastapi as p
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGO_URI: str


settings = Settings()


@lru_cache()
def create_settings() -> Settings:
    return settings


SettingsDep = t.Annotated[Settings, p.Depends(create_settings)]
