import typing as t
from enum import Enum

import pydantic as p
from openai.types.chat import ChatCompletionMessageParam

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID


class AIToolCallType(str, Enum):
    Function = "Function"


class AIMessageRole(str, Enum):
    User = "User"
    Assistant = "Assistant"
    System = "System"


class AIFunctionCall(p.BaseModel):
    arguments: str = p.Field(alias="arguments")
    name: str = p.Field(alias="name")


class AIToolCall(p.BaseModel):
    id: str = p.Field(alias="id")
    function: AIFunctionCall = p.Field(alias="function")
    type: t.Literal[AIToolCallType.Function] = p.Field(alias="type", default=AIToolCallType.Function)


class BaseAIMessage(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str | None = p.Field(alias="name", default=None)


class AIUserMessage(BaseAIMessage, p.BaseModel):
    content: str = p.Field(alias="content")
    role: t.Literal[AIMessageRole.User] = p.Field(alias="role", default=AIMessageRole.User)


class AISystemMessage(BaseAIMessage, p.BaseModel):
    content: str = p.Field(alias="content")
    role: t.Literal[AIMessageRole.System] = p.Field(alias="role", default=AIMessageRole.System)


class AIAssistantMessage(BaseAIMessage, p.BaseModel):
    content: str = p.Field(alias="content")
    role: t.Literal[AIMessageRole.Assistant] = p.Field(alias="role", default=AIMessageRole.Assistant)
    refusal: str | None = p.Field(alias="refusal", default=None)
    tool_calls: list[AIToolCall] | None = p.Field(alias="tool_calls", default=None)


AIMessage = AIUserMessage | AISystemMessage | AIAssistantMessage


class AIConversation(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete, p.BaseModel):
    name: str = p.Field(alias="name")
    bot_id: PyObjectUUID = p.Field(alias="bot_id")
    design_project_id: PyObjectUUID | None = p.Field(alias="design_project_id", default=None)
    user_id: PyObjectUUID = p.Field(alias="user_id")
    messages: list[AIMessage] = p.Field(alias="messages", default=[])
