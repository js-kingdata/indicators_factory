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
    def getex(cls, prefix, name):
        """
           Return the value at key ``prefix + ':' + name``, or None if the key doesn't exist
           prefix: The prefix parameter indicates the name value of the current crawler
           name: Customize the name value related to the current business
        """
        key = prefix + ':' + name

        if len(key.encode()) > 1024:
            logging.warning('Key is too large')
            return None
        value = _redis_client.get(key)
        if value:
            return str(value, encoding="utf-8")
        return value

    @classmethod
    def setex(cls, prefix, name: str, value: str, ttl):
        """
           Return the value at key ``prefix + ':' + name``, or None if the key doesn't exist
           prefix: The prefix parameter indicates the name value of the current crawler
           name: Customize the name value related to the current business. The key string size cannot exceed 1KB
           value: The stored value cannot exceed 128 KB
           ttl: Expiration time must be set, and value must be taken according to business requirements
        """
        key = prefix + ':' + name
        # Size limit, value cannot exceed 128 KB, key cannot exceed 1 KB
        if len(value.encode()) > 1024 * 128 or len(key.encode()) > 1024:
            logging.warning('Key or Value is too large')
            return False

        if _redis_client.get(key) is not None:
            return False

        if ttl:
            _redis_client.set(key, value, ex=ttl)
        else:
            _redis_client.set(key, value)
        return True

    @classmethod
    def get_and_set_key(cls, prefix, name: str, value: str, ttl: int = None):
        """
            Return the value at key ``prefix + ':' + name``, or True if the key exist
            prefix: The prefix parameter indicates the name value of the current crawler
            name: Customize the name value related to the current business. The key string size cannot exceed 1KB
            value: The stored value cannot exceed 128 KB
            ttl: Expiration time must be set, and value must be taken according to business requirements
         """
        key = prefix + ':' + name
        # Size limit, value cannot exceed 128 KB, key cannot exceed 1 KB
        if len(value.encode()) > 1024 * 128 or len(key.encode()) > 1024:
            logging.warning('Key or Value is too large')
            return False

        if _redis_client.get(name):
            return True
        _redis_client.set(name, value)
        if ttl:
            _redis_client.expire(name, ttl)

    @classmethod
    def thing_lock(cls, name, expiration_time=2, time_out=3):
        """
        code pessimistic locking
        Function: Avoid simultaneous execution of functions, resulting in unpredictable problems
        """
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
