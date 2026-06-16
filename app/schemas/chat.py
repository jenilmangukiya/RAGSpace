from pydantic import BaseModel


class ChatRequest(BaseModel):
    app_id: str
    query: str


class ChatSource(BaseModel):
    document_id: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
