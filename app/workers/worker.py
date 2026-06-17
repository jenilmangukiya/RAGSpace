from arq.connections import RedisSettings
from app.workers.tasks import process_document
from app.core.config import settings


class WorkerSettings:
    functions = [
        process_document,
    ]

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    # ⏱️ Check Redis every 5 seconds instead of aggressively polling
    poll_delay = 15.0
