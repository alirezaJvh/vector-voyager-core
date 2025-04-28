import redis.asyncio as redis

from common.config import get_settings

settings = get_settings()

redis_client: redis.Redis = None


async def get_client() -> redis.Redis:
    if not redis_client:
        try:
            return await redis.from_url(
                f"redis://redis:{settings.REDIS_PORT}/0",
                decode_responses=True,
            )
        except redis.Redis.RedisError as e:
            raise e
    return redis_client

    