from app.services.query_service import QueryService
from app.services.embedding_service import (
    EmbeddingService,
)
from app.services.qdrant_service import (
    QdrantService,
)


class SearchService:

    @staticmethod
    def search(
        query: str,
        user_id: str,
        app_id: str,
    ):
        query_embedding = EmbeddingService.create_embedding(query)

        query_type = QueryService.classify_query(query)

        if query_type == "document":
            results = QdrantService.search_document_summary(
                query_vector=query_embedding,
                user_id=user_id,
                app_id=app_id,
            )

        else:
            results = QdrantService.search(
                query_vector=query_embedding,
                user_id=user_id,
                app_id=app_id,
            )

        return [
            {
                "score": hit.score,
                "text": hit.payload["text"],
                "document_id": hit.payload["document_id"],
                "chunk_index": hit.payload["chunk_index"],
                "page_number": hit.payload.get("page_number"),
            }
            for hit in results
        ]
