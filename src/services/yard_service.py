from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import HTTPException
from pydantic import BaseModel

from src.common.models.yard import YardModel
from src.database.mongodb import MongoDbDep
from src.logger import LoggerDep


class YardCreateRequest(BaseModel):
    name: str


class YardUpdateRequest(BaseModel):
    name: Optional[str] = None


class YardService:
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._db = db
        self._logger = logger

    @staticmethod
    async def create(data: YardCreateRequest) -> YardModel:
        yard = YardModel(name=data.name)
        await yard.create()
        return yard

    @staticmethod
    async def get_by_id(yard_id: PydanticObjectId) -> YardModel:
        yard = await YardModel.get(yard_id)
        if not yard:
            raise HTTPException(status_code=404, detail="Yard not found")
        return yard

    @staticmethod
    async def list_all() -> List[YardModel]:
        return await YardModel.find_all().to_list()

    @staticmethod
    async def update(yard_id: PydanticObjectId, data: YardUpdateRequest) -> YardModel:
        yard = await YardModel.get(yard_id)
        if not yard:
            raise HTTPException(status_code=404, detail="Yard not found")

        if data.name:
            yard.name = data.name

        await yard.save()
        return yard

    @staticmethod
    async def delete(yard_id: PydanticObjectId) -> None:
        yard = await YardModel.get(yard_id)
        if not yard:
            raise HTTPException(status_code=404, detail="Yard not found")
        await yard.delete()
