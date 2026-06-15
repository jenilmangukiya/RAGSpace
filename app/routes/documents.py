from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_document(
    app_id: UUID,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    return await service.upload_document(
        app_id=app_id,
        file=file,
        user_id=current_user["id"],
    )


@router.get(
    "/{app_id}",
    response_model=list[DocumentResponse],
)
def get_documents(
    app_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    return service.get_documents(
        app_id=app_id,
        user_id=current_user["id"],
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    service.delete_document(
        document_id=document_id,
        user_id=current_user["id"],
    )

    return {"message": "Document deleted"}
