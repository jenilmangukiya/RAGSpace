from fastapi.responses import StreamingResponse

from app.integrations.openai import OpenAIClient
from app.schemas.chat import ChatRequest
from app.services.search_service import SearchService
from app.schemas.chat import ChatResponse
from fastapi import Depends
from app.core.auth import get_current_user
from fastapi import APIRouter
from app.services.chat_service import ChatService


router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
):
    result = ChatService.chat(
        question=payload.query,
        user_id=str(current_user["id"]),
        app_id=str(payload.app_id),
        history=payload.history,
    )

    return result


@router.post("/stream")
def stream_chat(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
):

    generator = ChatService.stream_chat(
        question=payload.query,
        history=payload.history,
        user_id=current_user["id"],
        app_id=str(payload.app_id),
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
    )
