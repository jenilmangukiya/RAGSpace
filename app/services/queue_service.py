from app.workers.redis import get_redis_pool


class QueueService:
    @staticmethod
    async def enqueue_document(
        document_id: str,
    ):
        redis = await get_redis_pool()

        await redis.enqueue_job(
            "process_document",
            document_id,
        )
