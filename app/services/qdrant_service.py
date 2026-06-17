import uuid

from qdrant_client.http.models import FilterSelector
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from app.integrations.qdrant import qdrant


class QdrantService:
    @staticmethod
    def upsert_chunks(
        chunks,
        vectors,
        user_id,
        app_id,
        document_id,
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
                        "chunk_index": index,
                        "text": chunk,
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
        limit: int = 5,
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
