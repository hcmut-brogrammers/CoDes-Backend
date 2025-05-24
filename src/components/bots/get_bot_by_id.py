import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import BotModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetBotById = IBaseComponent["GetBotById.Request", "GetBotById.Response"]


class GetBotById(IGetBotById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.BOTS)
        self._logger = logger

    class Request(BaseModel):
        bot_id: PyObjectUUID

    class Response(p.BaseModel):
        bot: BotModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        bot_data = self._collection.find_one({"_id": request.bot_id})
        if not bot_data:
            self._logger.error(f"Bot with id {request.bot_id} not found.")
            raise NotFoundError(f"Bot with id {request.bot_id} not found.")

        bot = BotModel(**bot_data)
        return self.Response(bot=bot)


GetBotByIdDep = t.Annotated[GetBotById, Depends()]
