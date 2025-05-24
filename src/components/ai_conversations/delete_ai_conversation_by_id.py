import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import AIConversation, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IDeleteAIConversationById = IBaseComponent["DeleteAIConversationById.Request", "DeleteAIConversationById.Response"]


class DeleteAIConversationById(IDeleteAIConversationById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.AI_CONVERSATIONS)
        self._logger = logger

    class Request(BaseModel):
        ai_conversation_id: PyObjectUUID

    class Response(p.BaseModel):
        deleted_ai_conversation: AIConversation

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        ai_conversation_id = request.ai_conversation_id
        ai_conversation_data = self._collection.find_one({"_id": ai_conversation_id})
        if not ai_conversation_data:
            self._logger.error(f"Bot with id {ai_conversation_id} not found.")
            raise NotFoundError(f"Bot with id {ai_conversation_id} not found.")

        ai_conversation = AIConversation(**ai_conversation_data)
        ai_conversation.is_deleted = True
        ai_conversation.deleted_at = get_utc_now()
        self._collection.update_one({"_id": ai_conversation.id}, {"$set": ai_conversation.model_dump(exclude={"id"})})
        return self.Response(deleted_ai_conversation=ai_conversation)


DeleteAIConversationByIdDep = t.Annotated[DeleteAIConversationById, Depends()]
