from app.integrations.storage import supabase
from app.services.qdrant_service import QdrantService
from app.models import Document
from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.app import App


class AppService:
    def __init__(self, db: Session):
        self.db = db

    # Create new App
    async def create_app(self, name: str, user_id: UUID) -> App:
        app = App(name=name, user_id=user_id)

        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)

        return app

    async def get_apps(self, user_id: UUID) -> list[App]:
        apps = (
            self.db.query(
                App,
                func.count(Document.id).label("document_count"),
            )
            .join(Document, Document.app_id == App.id, isouter=True)
            .filter(App.user_id == user_id)
            .order_by(App.created_at.desc())
            .group_by(App.id)
            .all()
        )

        return [
            {
                "id": app.id,
                "name": app.name,
                "created_at": app.created_at,
                "document_count": document_count,
            }
            for app, document_count in apps
        ]

    async def get_app(self, app_id: UUID, user_id: UUID) -> App:
        app = (
            self.db.query(App).filter(App.id == app_id, App.user_id == user_id).first()
        )

        if not app:
            raise HTTPException(
                status_code=404,
                detail=f"App with id {app_id} not found",
            )

        return app

    async def delete_app(self, app_id: UUID, user_id: UUID):
        app = (
            self.db.query(App).filter(App.id == app_id, App.user_id == user_id).first()
        )

        if not app:
            return False

        documents = (
            self.db.query(Document)
            .filter(
                Document.app_id == app_id,
            )
            .all()
        )

        # Delete all vectors for the app
        try:
            QdrantService.delete_app_chunks(str(app_id))
        except Exception as e:
            print(f"Failed to delete app vectors: {e}")

        # Delete files from storage
        storage_paths = [
            document.storage_path for document in documents if document.storage_path
        ]

        if storage_paths:
            try:
                supabase.storage.from_("documents").remove(storage_paths)
            except Exception as e:
                print(f"Failed to delete files: {e}")

        self.db.delete(app)
        self.db.commit()

        return True
