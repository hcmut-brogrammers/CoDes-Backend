from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.common.models.house import HouseModel
from src.services.house_service import HouseCreateRequest, HouseService, HouseUpdateRequest

router = APIRouter(prefix="/houses", tags=["Houses"])


@router.post("/", response_model=HouseModel, status_code=status.HTTP_201_CREATED)
async def create_house(request: HouseCreateRequest):
    return await HouseService.create(request)


@router.get("/", response_model=List[HouseModel])
async def list_houses():
    return await HouseService.list_all()


@router.get("/{house_id}", response_model=HouseModel)
async def get_house(house_id: PydanticObjectId):
    return await HouseService.get_by_id(house_id)


@router.put("/{house_id}", response_model=HouseModel)
async def update_house(house_id: PydanticObjectId, request: HouseUpdateRequest):
    return await HouseService.update(house_id, request)


@router.delete("/{house_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_house(house_id: PydanticObjectId):
    await HouseService.delete(house_id)
