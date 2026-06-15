from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings


def get_redis_settings():
    return RedisSettings.from_dsn(settings.REDIS_URL)


async def get_redis_pool():
    return await create_pool(get_redis_settings())
