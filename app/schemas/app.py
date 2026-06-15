from pydantic import Field
from pydantic import BaseModel
from uuid import UUID


class CreateAppRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class AppResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
