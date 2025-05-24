import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import BotConfig, BotModel, LLMProvider
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

ICreateBot = IBaseComponent["CreateBot.Request", "CreateBot.Response"]


class CreateBot(ICreateBot):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.BOTS)
        self._logger = logger

    class Request(BaseModel):
        name: str
        provider: LLMProvider
        config: BotConfig

    class Response(p.BaseModel):
        created_bot: BotModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        bot = BotModel(name=request.name, provider=request.provider, config=request.config)
        bot_data = bot.model_dump(by_alias=True)
        insert_one_result = self._collection.insert_one(bot_data)
        created_bot_data = self._collection.find_one({"_id": insert_one_result.inserted_id})
        if not created_bot_data:
            self._logger.error(
                f"Insert bot data with id {insert_one_result.inserted_id} successfully, but unable to find the created bot"
            )
            raise InternalServerError("Insert bot data successfully, but unable to find the created bot")

        return self.Response(created_bot=bot)


CreateBotDep = t.Annotated[CreateBot, Depends()]
