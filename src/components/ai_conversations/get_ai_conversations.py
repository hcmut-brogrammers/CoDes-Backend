import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import AIConversation, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetAIConversations = IBaseComponent["GetAIConversations.Request", "GetAIConversations.Response"]


class GetAIConversations(IGetAIConversations):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.AI_CONVERSATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(BaseModel):
        design_project_id: PyObjectUUID

    class Response(p.BaseModel):
        ai_conversations: list[AIConversation]

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        user_id = self._user_context.user_id
        design_project_id = request.design_project_id
        ai_conversations_data = self._collection.find({"user_id": user_id, "design_project_id": design_project_id})
        if not ai_conversations_data:
            self._logger.error(f"AI conversations for user {user_id} and design project {design_project_id} not found.")
            raise NotFoundError(
                f"AI conversations for user {user_id} and design project {design_project_id} not found."
            )

        ai_conversations = [AIConversation(**ai_conversation_data) for ai_conversation_data in ai_conversations_data]
        return self.Response(ai_conversations=ai_conversations)


GetAIConversationsDep = t.Annotated[GetAIConversations, Depends()]
