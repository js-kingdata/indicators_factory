import logging

import redis
import time

from crawlers.config import REDIS_URL
from urllib.parse import urlparse

_REDIS_URL = urlparse(REDIS_URL)

pool = redis.connection.ConnectionPool(
    host=_REDIS_URL.hostname,
    port=_REDIS_URL.port,
    db=_REDIS_URL.path[1:],
)

_redis_client = redis.Redis(connection_pool=pool)


class rds:

    @classmethod
    def get(cls, prefix, name):
        """获取指定 [name] 的值"""
        if len((prefix + name).encode()) > 1024:
            logging.warning('Key is too large')
            return None
        value = _redis_client.get(prefix + name)
        if value:
            return str(value, encoding="utf-8")
        return value

    @classmethod
    def set(cls, prefix: str, name: str, value: str, ttl):
        # 大小限制，value 不能超过 128 KB, key 不能超过 1 KB
        if len(value.encode()) > 1024 * 128 or len((prefix + name).encode()) > 1024:
            logging.warning('Key or Value is too large')
            return True

        _redis_client.set(prefix + name, value)
        if ttl:
            _redis_client.expire(prefix + name, ttl)

    @classmethod
    def thing_lock(cls, name, expiration_time=2, time_out=3):
        def outer_func(func):
            def wrapper_func(*args, **kwargs):
                lock_name = f'lock:{name}'
                end_time = time.time() + time_out
                while time.time() < end_time:
                    if _redis_client.setnx(lock_name, expiration_time):
                        _redis_client.expire(lock_name, expiration_time)
                        data = func(*args, **kwargs)
                        _redis_client.delete(lock_name)
                        return data
                    time.sleep(0.001)
                return func(*args, **kwargs)

            return wrapper_func

        return outer_func
