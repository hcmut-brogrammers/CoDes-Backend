import typing as t

from fastapi import Depends
from openai import AsyncOpenAI

from ....config import SettingsDep


def get_openai_client(settings: SettingsDep) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


OpenAIClientDep = t.Annotated[AsyncOpenAI, Depends(get_openai_client)]
