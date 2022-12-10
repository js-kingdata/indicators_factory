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
    def get(cls, name):
        """获取指定 [name] 的值"""
        value = _redis_client.get(name)
        if value:
            return str(value, encoding="utf-8")
        return value

    @classmethod
    def set(cls, name, value, ttl: int = None):
        _redis_client.set(name, value)
        if ttl:
            _redis_client.expire(name, ttl)

    @classmethod
    def hget(cls, name, key):
        return _redis_client.hget(name, key)

    @classmethod
    def hset(cls, name, key, value):
        return _redis_client.hset(name, key, value)

    @classmethod
    def srandmember(cls, name):
        return _redis_client.srandmember(name, 1)

    @classmethod
    def set_sismember_check(cls, name, member):
        if _redis_client.sismember(name, member):
            return True
        _redis_client.sadd(name, member)

    @classmethod
    def get_and_set_key(cls, name, value=time.time(), ttl: int = None):
        if _redis_client.get(name):
            return True
        _redis_client.set(name, value)
        if ttl:
            _redis_client.expire(name, ttl)

    @classmethod
    def set_multi_member_chick(cls, name, multi_member: set, separator='"', ttl=None):
        new_multi_member = set()
        redis_data = _redis_client.get(name)
        if redis_data:
            old_multi_member = set(bytes.decode(redis_data).split('"'))
            new_multi_member = multi_member - old_multi_member
            multi_member |= old_multi_member
        _redis_client.set(name, str(separator.join(multi_member)))
        if ttl:
            _redis_client.expire(name, ttl)
        return new_multi_member

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
