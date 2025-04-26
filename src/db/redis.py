import redis.asyncio as redis
from .config import REDIS_PORT

redis_client: redis.Redis = None


async def get_redis() -> redis.Redis:
    global redis_client
    
    if not redis_client:
        try:
            redis_instance = await redis.from_url(
                f"redis://redis:{REDIS_PORT}",
                decode_responses=True,
            )
        except redis.Redis.RedisError as e:
            # TODO: app logger 
            # app_logger.error(f"Error connecting to Redis: {e}")
            print('### error')
            raise e
    return redis_instance