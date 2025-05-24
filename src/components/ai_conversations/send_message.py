import asyncio
import json
import typing as t

import pydantic as p
from fastapi import Depends
from fastapi.responses import StreamingResponse
from openai.lib.streaming.chat import AsyncChatCompletionStreamManager
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from starlette.responses import ContentStream

from ...common.models import AIAssistantMessage, AIMessage, AIMessageRole, AIUserMessage, PyObjectUUID
from ...common.structured_outputs import ParsedCircleModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, OpenAIClientDep
from ...exceptions import InternalServerError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from ..bots import GetBotByIdDep
from .get_ai_conversation import GetAIConversationDep

ISendMessage = IBaseComponent["SendMessage.Request", "StreamingResponse"]


class MessageChunk(p.BaseModel):
    user_message: AIUserMessage
    response_message: AIAssistantMessage
    error: str | None = None


CHUNK_SEPARATOR = "\n\n"
DATA_PREFIX = "data: "
DELAY_SEC = 0.1


class SendMessage(ISendMessage):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        get_ai_conversation: GetAIConversationDep,
        get_bot_by_id: GetBotByIdDep,
        openai_client: OpenAIClientDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.AI_CONVERSATIONS)
        self._logger = logger
        self._get_ai_conversation = get_ai_conversation
        self._get_bot_by_id = get_bot_by_id
        self._openai_client = openai_client

    class HttpRequest(p.BaseModel):
        content: str

    class Request(HttpRequest, p.BaseModel):
        ai_conversation_id: PyObjectUUID

    async def aexecute(self, request: "Request") -> "StreamingResponse":
        self._logger.info(execute_service_method(self))
        ai_conversation_id = request.ai_conversation_id
        get_ai_conversation_request = self._get_ai_conversation.Request(ai_conversation_id=ai_conversation_id)
        get_ai_conversation_response = await self._get_ai_conversation.aexecute(get_ai_conversation_request)
        ai_conversation = get_ai_conversation_response.ai_conversation

        get_bot_by_id_request = self._get_bot_by_id.Request(
            bot_id=ai_conversation.bot_id,
        )
        get_bot_by_id_response = await self._get_bot_by_id.aexecute(get_bot_by_id_request)
        bot = get_bot_by_id_response.bot

        user_message = AIUserMessage(content=request.content)
        messages = [*ai_conversation.messages, user_message]
        openai_messages = self.convert_openai_messages(messages)
        try:
            user_message_data = user_message.model_dump(by_alias=True, exclude_none=True)
            self._collection.update_one(
                {"_id": request.ai_conversation_id}, {"$push": {"messages": user_message_data}}, upsert=True
            )

            response_stream = self._openai_client.beta.chat.completions.stream(
                model=bot.config.model,
                messages=openai_messages,
                temperature=bot.config.temperature,
                top_p=bot.config.top_p,
                frequency_penalty=bot.config.frequency_penalty,
                presence_penalty=bot.config.presence_penalty,
                max_completion_tokens=bot.config.max_tokens,
                # NOTE: specify JSON-schema format for design generation
                response_format=ParsedCircleModel,
            )

            assistant_message = AIAssistantMessage(
                content="",
            )
            assistant_message_data = assistant_message.model_dump(by_alias=True, exclude_none=True)
            self._collection.update_one(
                {"_id": request.ai_conversation_id}, {"$push": {"messages": assistant_message_data}}, upsert=True
            )
            content_stream = self.make_content_stream(
                response_stream, ai_conversation_id, user_message, assistant_message
            )
            stream_response = StreamingResponse(
                content_stream,
                media_type="text/event-stream",
                headers={"Content-Type": "text/event-stream"},
                status_code=200,
            )

            return stream_response
        except Exception as e:
            self._logger.error(f"Error while sending message: {e}")
            raise InternalServerError("Error while sending message") from e

    def convert_openai_messages(self, messages: list[AIMessage]) -> list[ChatCompletionMessageParam]:
        openai_messages: list[ChatCompletionMessageParam] = []
        for message in messages:
            if message.role == AIMessageRole.User:
                user_message: ChatCompletionUserMessageParam = {
                    "role": "user",
                    "content": message.content,
                }
                if message.name:
                    user_message["name"] = message.name

                openai_messages.append(user_message)
            elif message.role == AIMessageRole.System:
                system_message: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": message.content,
                }
                if message.name:
                    user_message["name"] = message.name

                openai_messages.append(system_message)
            elif message.role == AIMessageRole.Assistant:
                assistant_message: ChatCompletionAssistantMessageParam = {
                    "role": "assistant",
                    "content": message.content,
                }
                if message.tool_calls:
                    openai_tool_calls: list[ChatCompletionMessageToolCallParam] = []
                    for tool_call in message.tool_calls:
                        openai_tool_call: ChatCompletionMessageToolCallParam = {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                            "type": "function",
                        }
                        openai_tool_calls.append(openai_tool_call)
                    assistant_message["tool_calls"] = openai_tool_calls
                if message.name:
                    user_message["name"] = message.name

                openai_messages.append(assistant_message)
        return openai_messages

    async def make_content_stream(
        self,
        response_stream: AsyncChatCompletionStreamManager[ParsedCircleModel],
        ai_conversation_id: PyObjectUUID,
        user_message: AIUserMessage,
        assistant_message: AIAssistantMessage,
    ) -> ContentStream:
        assistant_message_id = assistant_message.id
        async with response_stream as stream:
            async for event in stream:
                if event.type == "content.delta":
                    parsed = event.parsed
                    if parsed is not None:
                        parsed_content = json.dumps(parsed)
                        assistant_message.content = parsed_content
                        # Print the parsed data as JSON
                        # print("content.delta parsed:", parsed)

                        # NOTE: update assistant message content
                        self._collection.update_one(
                            {"_id": ai_conversation_id},
                            {"$set": {"messages.$[message].content": parsed_content}},
                            array_filters=[{"message._id": assistant_message_id}],
                        )
                        message_chunk = MessageChunk(user_message=user_message, response_message=assistant_message)
                        serialized_message_chunk = self.serialize_message_chunk(message_chunk)
                        yield serialized_message_chunk
                        await asyncio.sleep(DELAY_SEC)
                elif event.type == "content.done":
                    print("content.done")
                elif event.type == "error":
                    print("Error in stream:", event.error)

    def serialize_message_chunk(self, chunk: MessageChunk) -> str:
        return f"{DATA_PREFIX}{json.dumps(chunk.model_dump(mode='json', exclude_none=True))}{CHUNK_SEPARATOR}"


SendMessageDep = t.Annotated[SendMessage, Depends()]
