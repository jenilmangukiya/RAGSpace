import uuid

from qdrant_client.http.models import FilterSelector
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from app.integrations.qdrant import qdrant


MIN_SCORE = 0.5


class QdrantService:
    @staticmethod
    def upsert_chunks(
        chunks, vectors, user_id, app_id, document_id, document_name, type
    ):
        points = []

        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "app_id": app_id,
                        "document_id": document_id,
                        "chunk_index": index + 1,
                        "text": chunk["chunk_content"],
                        "page_number": chunk["page_number"],
                        "document_name": document_name,
                        "type": type,
                    },
                )
            )

        qdrant.upsert(
            collection_name="documents",
            points=points,
        )

    @staticmethod
    def search(
        query_vector: list[float],
        user_id: str,
        app_id: str,
        limit: int = 15,
    ):
        results = qdrant.query_points(
            collection_name="documents",
            query=query_vector,
            limit=limit,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=str(user_id)),
                    ),
                    FieldCondition(
                        key="app_id",
                        match=MatchValue(value=str(app_id)),
                    ),
                ]
            ),
        )

        filtered = [point for point in results.points if point.score >= MIN_SCORE]
        return filtered

    @staticmethod
    def search_document_summary(
        query_vector: list[float],
        user_id: str,
        app_id: str,
    ):
        results = qdrant.query_points(
            collection_name="documents",
            query=query_vector,
            limit=5,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=str(user_id)),
                    ),
                    FieldCondition(
                        key="app_id",
                        match=MatchValue(value=str(app_id)),
                    ),
                    FieldCondition(
                        key="type",
                        match=MatchValue(value="document_summary"),
                    ),
                ]
            ),
        )

        return results.points

    @staticmethod
    def delete_document_chunks(
        document_id: str,
    ):
        qdrant.delete(
            collection_name="documents",
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(
                                value=document_id,
                            ),
                        ),
                    ]
                )
            ),
        )

    @staticmethod
    def delete_app_chunks(app_id: str):
        qdrant.delete(
            collection_name="documents",
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="app_id",
                            match=MatchValue(
                                value=app_id,
                            ),
                        ),
                    ]
                )
            ),
        )
