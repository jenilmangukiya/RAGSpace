from uuid import UUID

from pydantic import BaseModel


class SearchRequest(BaseModel):
    app_id: UUID
    query: str


class SearchResult(BaseModel):
    score: float
    text: str
    document_id: str
    chunk_index: int


class SearchResponse(BaseModel):
    results: list[SearchResult]
