from uuid import UUID

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    app_id: UUID


class ConversationResponse(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class ConversationUpdate(BaseModel):
    title: str
