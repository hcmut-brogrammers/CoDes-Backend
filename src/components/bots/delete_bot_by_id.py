import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import BotModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IDeleteBotById = IBaseComponent["DeleteBotById.Request", "DeleteBotById.Response"]


class DeleteBotById(IDeleteBotById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.BOTS)
        self._logger = logger

    class Request(BaseModel):
        bot_id: PyObjectUUID

    class Response(p.BaseModel):
        deleted_bot: BotModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        bot_data = self._collection.find_one({"_id": request.bot_id})
        if not bot_data:
            self._logger.error(f"Bot with id {request.bot_id} not found.")
            raise NotFoundError(f"Bot with id {request.bot_id} not found.")

        bot = BotModel(**bot_data)
        bot.is_deleted = True
        bot.deleted_at = get_utc_now()
        self._collection.update_one({"_id": bot.id}, {"$set": bot.model_dump(exclude={"id"})})

        return self.Response(deleted_bot=bot)


DeleteBotByIdDep = t.Annotated[DeleteBotById, Depends()]
