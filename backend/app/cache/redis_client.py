import redis.asyncio as redis
from app.config import settings

class RedisClient:
    def __init__(self):
        self._pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get_client(self):
        return redis.Redis(connection_pool=self._pool)

redis_client = RedisClient()

async def get_redis():
    return redis_client.get_client()
