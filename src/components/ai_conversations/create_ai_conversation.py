import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import AIConversation, AIMessage, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

ICreateAIConversation = IBaseComponent["CreateAIConversation.Request", "CreateAIConversation.Response"]


class CreateAIConversation(ICreateAIConversation):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.AI_CONVERSATIONS)
        self._logger = logger

    class Request(BaseModel):
        name: str
        bot_id: PyObjectUUID
        design_project_id: PyObjectUUID
        user_id: PyObjectUUID
        messages: list[AIMessage] = []

    class Response(p.BaseModel):
        created_ai_conversation: AIConversation

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        ai_conversation = AIConversation(
            name=request.name,
            bot_id=request.bot_id,
            design_project_id=request.design_project_id,
            user_id=request.user_id,
            messages=request.messages,
        )
        ai_conversation_data = ai_conversation.model_dump(by_alias=True)
        insert_one_result = self._collection.insert_one(ai_conversation_data)
        created_ai_conversation_data = self._collection.find_one({"_id": insert_one_result.inserted_id})
        if not created_ai_conversation_data:
            self._logger.error(
                f"Insert AI conversation data with id {insert_one_result.inserted_id} successfully, but unable to find the created AI conversation"
            )
            raise InternalServerError(
                "Insert AI conversation data successfully, but unable to find the created AI conversation"
            )

        return self.Response(created_ai_conversation=ai_conversation)


CreateAIConversationDep = t.Annotated[CreateAIConversation, Depends()]
