import uuid

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.app import App
from app.models.document import Document
from app.integrations.storage import supabase


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    async def upload_document(self, app_id: uuid.UUID, file: UploadFile, user_id: str):
        app = (
            self.db.query(App)
            .filter(App.id == app_id)
            .filter(App.user_id == user_id)
            .first()
        )

        if not app:
            raise HTTPException(status_code=404, detail="App not found")

        document = Document(
            app_id=app_id,
            file_name=file.filename,
            storage_path="temp",
            status="uploaded",
        )

        self.db.add(document)
        self.db.flush()

        storage_path = f"{user_id}/" f"{app_id}/" f"{document.id}"

        file_bytes = file.file.read()

        supabase.storage.from_("documents").upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": file.content_type,
            },
        )

        document.storage_path = storage_path

        self.db.commit()
        self.db.refresh(document)

        return document

    def get_documents(self, app_id: uuid.UUID, user_id: str):
        app = (
            self.db.query(App)
            .filter(App.id == app_id)
            .filter(App.user_id == user_id)
            .first()
        )

        if not app:
            raise HTTPException(
                status_code=404,
                detail="App not found",
            )

        return (
            self.db.query(Document)
            .filter(Document.app_id == app_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def delete_document(
        self,
        document_id: uuid.UUID,
        user_id: str,
    ):
        document = (
            self.db.query(Document)
            .join(App)
            .filter(
                Document.id == document_id,
                App.user_id == user_id,
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        supabase.storage.from_("documents").remove([document.storage_path])

        self.db.delete(document)
        self.db.commit()

        return True
