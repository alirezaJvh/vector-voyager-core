import redis.asyncio as redis
from .config import REDIS_PORT

class RedisClient:
    def __init__(self):
        self._client = None

    async def init_client(self):
        if not self._client:
            try:
                self._client = await redis.from_url(
                    f"redis://redis:{REDIS_PORT}",
                    decode_responses=True,
                )
            except redis.Redis.RedisError as e:
                # TODO: app logger 
                # app_logger.error(f"Error connecting to Redis: {e}")
                print('### error')
                raise e

    async def get_client(self) -> redis.Redis:
        if not self._client:
            await self.init_client()
        return self._client
    
        


    