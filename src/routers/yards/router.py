from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.common.models.yard import YardModel
from src.services.yard_service import YardCreateRequest, YardService, YardUpdateRequest

router = APIRouter(prefix="/yards", tags=["Yards"])


@router.post("/", response_model=YardModel, status_code=status.HTTP_201_CREATED)
async def create_yard(request: YardCreateRequest):
    return await YardService.create(request)


@router.get("/", response_model=List[YardModel])
async def list_yards():
    return await YardService.list_all()


@router.get("/{yard_id}", response_model=YardModel)
async def get_yard(yard_id: PydanticObjectId):
    return await YardService.get_by_id(yard_id)


@router.put("/{yard_id}", response_model=YardModel)
async def update_yard(yard_id: PydanticObjectId, request: YardUpdateRequest):
    return await YardService.update(yard_id, request)


@router.delete("/{yard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_yard(yard_id: PydanticObjectId):
    await YardService.delete(yard_id)
