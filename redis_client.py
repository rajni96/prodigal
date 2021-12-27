import redis


class RedisConnection:
    _redis_client = None

    def __new__(cls, *args, **kwargs):
        print("Redis connection")
        if cls._redis_client is None:
            cls._redis_client = super().__new__(cls, *args, **kwargs)
            pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
            cls._redis_client = redis.Redis(connection_pool=pool)
        return cls._redis_client
