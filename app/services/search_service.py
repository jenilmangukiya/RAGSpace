from app.services.reranker_service import RerankerService
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

        results = QdrantService.search(
            query_vector=query_embedding,
            user_id=user_id,
            app_id=app_id,
        )

        # Will recalculate scores and sort the order of it and give top 5
        rerank_results = RerankerService.rerank(
            query=query,
            search_results=results,
            top_k=5,
        )

        return [
            {
                "score": hit.score,
                "text": hit.payload["text"],
                "document_id": hit.payload["document_id"],
                "chunk_index": hit.payload["chunk_index"],
                "page_number": hit.payload.get("page_number"),
            }
            for hit in rerank_results
        ]
