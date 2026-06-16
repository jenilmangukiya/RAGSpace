from app.core.config import settings
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.services.app_service import AppService
from app.db.dependencies import get_db
from app.core.auth import get_current_user
from app.schemas.app import CreateAppRequest, AppResponse
from app.models.app import App


router = APIRouter()


@router.post("/", response_model=AppResponse)
async def create_app(
    payload: CreateAppRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AppService(db)

    return await service.create_app(payload.name, current_user["id"])


@router.get("/")
async def get_all_apps(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AppService(db)

    return await service.get_apps(current_user["id"])


@router.get("/{app_id}")
async def get_app(
    app_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AppService(db)
    return await service.get_app(app_id, current_user["id"])


@router.delete("/{app_id}")
async def delete_app(
    app_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AppService(db)

    deleted = await service.delete_app(app_id, current_user["id"])

    if not deleted:
        raise HTTPException(status_code=404, detail="App not found")

    return {"message": "App deleted"}
