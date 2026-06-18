from app.db.dependencies import get_db
from sqlalchemy.orm import Session
from app.services.conversation_service import ConversationService
from app.core.auth import get_current_user
from fastapi import APIRouter, Depends

from app.schemas.conversation import ConversationUpdate

router = APIRouter()


@router.post("/{app_id}")
def create_conversation(
    app_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    service = ConversationService(db)
    result = service.create_conversation(app_id, current_user["id"])

    return result


@router.get("/")
def get_conversations(
    app_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    service = ConversationService(db)
    results = service.list_conversations(app_id, current_user["id"])

    return results


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)
    results = service.get_conversation(conversation_id, current_user["id"])

    return results


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)
    result = service.delete_conversation(conversation_id, current_user["id"])

    return result


@router.put("/{conversation_id}")
def rename_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)
    result = service.rename_conversation(
        conversation_id, payload.title, current_user["id"]
    )

    return result
