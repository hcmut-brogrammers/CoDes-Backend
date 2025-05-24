import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import AIConversation, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetAIConversation = IBaseComponent["GetAIConversation.Request", "GetAIConversation.Response"]


class GetAIConversation(IGetAIConversation):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.AI_CONVERSATIONS)
        self._logger = logger

    class Request(BaseModel):
        ai_conversation_id: PyObjectUUID

    class Response(p.BaseModel):
        ai_conversation: AIConversation

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        ai_conversation_data = self._collection.find_one({"_id": request.ai_conversation_id})
        if not ai_conversation_data:
            self._logger.error(f"AI conversation with id {request.ai_conversation_id} not found.")
            raise NotFoundError(f"AI conversation with id {request.ai_conversation_id} not found.")

        ai_conversation = AIConversation(**ai_conversation_data)
        return self.Response(ai_conversation=ai_conversation)


GetAIConversationDep = t.Annotated[GetAIConversation, Depends()]
