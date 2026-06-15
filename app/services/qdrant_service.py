import uuid

from qdrant_client.models import PointStruct

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
