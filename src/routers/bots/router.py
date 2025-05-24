from fastapi import APIRouter, status

from ...common.models import PyObjectUUID
from ...components.bots import CreateBot, CreateBotDep, DeleteBotById, DeleteBotByIdDep, GetBotById, GetBotByIdDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.BOTS,
    tags=["bots"],
)


@router.post(
    "",
    response_model=CreateBot.Response,
    response_description="Bot created successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_bot(
    create_bot: CreateBotDep,
    request: CreateBot.Request,
):
    return await create_bot.aexecute(request)


@router.get(
    "/{bot_id}",
    response_model=GetBotById.Response,
    response_description="Bot retrieved successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_bot_by_id(
    get_bot_by_id: GetBotByIdDep,
    bot_id: PyObjectUUID,
):
    return await get_bot_by_id.aexecute(GetBotById.Request(bot_id=bot_id))


@router.delete(
    "/{bot_id}",
    response_model=DeleteBotById.Response,
    response_description="Bot deleted successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_bot_by_id(
    delete_bot_by_id: DeleteBotByIdDep,
    bot_id: PyObjectUUID,
):
    return await delete_bot_by_id.aexecute(DeleteBotById.Request(bot_id=bot_id))
