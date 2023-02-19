import redis.asyncio as redis

class RedisWrapper():
    def __init__(self, redis_url):
        self.redis_conn = redis.from_url(redis_url, decode_responses=True)

    def connect(self):
        return self.redis_conn