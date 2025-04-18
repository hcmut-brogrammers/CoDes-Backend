from typing import List, Optional
from uuid import UUID

from beanie import PydanticObjectId
from fastapi import HTTPException
from pydantic import BaseModel

from src.common.models.house import HouseModel
from src.common.models.yard import YardModel


class HouseCreateRequest(BaseModel):
    name: str
    yard_id: PydanticObjectId


class HouseUpdateRequest(BaseModel):
    name: Optional[str] = None
    yard_id: Optional[PydanticObjectId] = None


class HouseService:

    @staticmethod
    async def create(data: HouseCreateRequest) -> HouseModel:
        yard = await YardModel.get(data.yard_id)
        if not yard:
            raise HTTPException(status_code=404, detail="Yard not found")

        house = HouseModel(name=data.name, yard=yard)
        await house.insert()
        return house

    @staticmethod
    async def get_by_id(house_id: PydanticObjectId) -> HouseModel:
        house = await HouseModel.get(house_id)
        if not house:
            raise HTTPException(status_code=404, detail="House not found")
        await house.fetch_link(HouseModel.yard)
        return house

    @staticmethod
    async def list_all() -> List[HouseModel]:
        houses = await HouseModel.find_all().to_list()
        for house in houses:
            await house.fetch_link(HouseModel.yard)
        return houses

    @staticmethod
    async def update(house_id: PydanticObjectId, data: HouseUpdateRequest) -> HouseModel:
        house = await HouseModel.get(house_id)
        if not house:
            raise HTTPException(status_code=404, detail="House not found")

        if data.name:
            house.name = data.name
        if data.yard_id:
            yard = await YardModel.get(data.yard_id)
            if not yard:
                raise HTTPException(status_code=404, detail="Yard not found")
            house.yard = yard

        await house.save()
        await house.fetch_link(HouseModel.yard)
        return house

    @staticmethod
    async def delete(house_id: PydanticObjectId) -> None:
        house = await HouseModel.get(house_id)
        if not house:
            raise HTTPException(status_code=404, detail="House not found")
        await house.delete()
