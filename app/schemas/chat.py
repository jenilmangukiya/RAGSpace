from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    app_id: str
    query: str
    history: list[ChatMessage] = []


class ChatSource(BaseModel):
    document_id: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
