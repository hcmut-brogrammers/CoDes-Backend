from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from ...common.models import PyObjectUUID
from ...components.ai_conversations import (
    CreateAIConversation,
    CreateAIConversationDep,
    DeleteAIConversationById,
    DeleteAIConversationByIdDep,
    GetAIConversation,
    GetAIConversationDep,
    GetAIConversations,
    GetAIConversationsDep,
    SendMessage,
    SendMessageDep,
)
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.AI_CONVERSATIONS,
    tags=["ai_conversations"],
)


@router.post(
    "",
    response_model=CreateAIConversation.Response,
    response_description="AI conversation created successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_ai_conversation(
    create_ai_conversation: CreateAIConversationDep,
    request: CreateAIConversation.Request,
):
    return await create_ai_conversation.aexecute(request)


@router.post(
    "/{ai_conversation_id}/send-message",
    response_description="AI conversation message sent successfully",
    status_code=status.HTTP_200_OK,
)
async def send_message(
    send_message: SendMessageDep,
    ai_conversation_id: PyObjectUUID,
    request: SendMessage.HttpRequest,
):
    return await send_message.aexecute(
        SendMessage.Request(ai_conversation_id=ai_conversation_id, content=request.content)
    )


@router.get(
    "",
    response_model=GetAIConversations.Response,
    response_description="AI conversations retrieved successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_ai_conversations(
    get_ai_conversations: GetAIConversationsDep,
    design_project_id: PyObjectUUID,
):
    return await get_ai_conversations.aexecute(GetAIConversations.Request(design_project_id=design_project_id))


@router.get(
    "/{ai_conversation_id}",
    response_model=GetAIConversation.Response,
    response_description="AI conversation retrieved successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_ai_conversation(
    get_ai_conversation: GetAIConversationDep,
    ai_conversation_id: PyObjectUUID,
):
    return await get_ai_conversation.aexecute(GetAIConversation.Request(ai_conversation_id=ai_conversation_id))


@router.delete(
    "/{ai_conversation_id}",
    response_model=DeleteAIConversationById.Response,
    response_description="AI conversation deleted successfully",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_ai_conversation_by_id(
    delete_bot_by_id: DeleteAIConversationByIdDep,
    ai_conversation_id: PyObjectUUID,
):
    return await delete_bot_by_id.aexecute(DeleteAIConversationById.Request(ai_conversation_id=ai_conversation_id))
