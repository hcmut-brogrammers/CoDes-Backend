from enum import Enum

import pydantic as p
from openai.types.chat import ChatCompletionMessageParam

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete


class LLMProvider(str, Enum):
    OPENAI = "openai"


class OpenAILLMModel(str, Enum):
    O4_MINI = "o4-mini"


class OpenAIBotConfig(p.BaseModel):
    model: OpenAILLMModel = p.Field(alias="model", default=OpenAILLMModel.O4_MINI)
    frequency_penalty: float | None = p.Field(alias="frequency_penalty", default=0.0)
    presence_penalty: float | None = p.Field(alias="presence_penalty", default=0.0)
    temperature: float | None = p.Field(alias="temperature", default=1.0)
    top_p: int | None = p.Field(alias="top_p", default=1)
    max_tokens: int | None = p.Field(alias="max_tokens", default=None)
    template: list[ChatCompletionMessageParam] = p.Field(alias="template", default=[])


BotConfig = OpenAIBotConfig


class BotModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete, p.BaseModel):
    name: str = p.Field(alias="name")
    provider: LLMProvider = p.Field(alias="provider", default=LLMProvider.OPENAI)
    config: BotConfig = p.Field(alias="config")
