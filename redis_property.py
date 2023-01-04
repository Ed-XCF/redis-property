import functools
from threading import RLock
from contextvars import ContextVar
from datetime import datetime

import orjson
from redis import Redis, RedisError

__all__ = ["redis_property", "cache_ttl", "cache_disable", "no_cache", "use_cache"]

_redis_cli = None
_default_cache_ttl = 24 * 60 * 60
_default_cache_disable = False

cache_ttl: ContextVar[int] = ContextVar('cache_ttl', default=_default_cache_ttl)
cache_disable: ContextVar[bool] = ContextVar('cache_disable', default=_default_cache_disable)


def _key_maker(obj, func):
    return type(obj).__name__ + func.__name__


def configure(url, *, key_maker=None, ttl=None, disable=None):
    global _redis_cli
    _redis_cli = Redis.from_url(url)

    if key_maker is not None:
        global _key_maker  # noqa
        _key_maker = key_maker

    if ttl is not None:
        cache_ttl.set(ttl)

    if disable is not None:
        cache_disable.set(disable)


def assert_redis_cli_exists():
    assert _redis_cli is not None, "Redis url has not been configured"


def safe_read(key):
    try:
        value = _redis_cli.get(key)
    except RedisError:
        return
    else:
        if value is None:
            return

        return value.decode()


def safe_write(key, value, ttl):
    try:
        return _redis_cli.set(key, value, ex=ttl, nx=True)
    except RedisError:
        return


def safe_remove(key):
    try:
        return _redis_cli.delete(key)
    except RedisError:
        return


class redis_property:  # noqa
    def __init__(self, seconds, key=None):
        assert_redis_cli_exists()

        if callable(seconds):
            self.func, self.ttl = seconds, cache_ttl.get()
        else:
            self.func, self.ttl = None, seconds

        self._key = key or _key_maker
        self._copy_func_info()
        self.lock = RLock()

    def __call__(self, func):
        if self.func is not None:
            if cache_disable.get():
                return self.func(func)
            
            return self.__get__(func, None)

        self.func = func
        self._copy_func_info()
        return self

    def _copy_func_info(self):
        if self.func is None:
            return

        for member_name in [
            "__doc__",
            "__name__",
            "__module__",
        ]:
            value = getattr(self.func, member_name)
            setattr(self, member_name, value)

    def __get__(self, instance, _):
        if cache_disable.get():
            return self.func(instance)
        
        if instance is None:
            return self

        key = self._make_key(instance)
        value = safe_read(key)
        if value is not None:
            return self._loads(value)

        with self.lock:
            value = safe_read(key)
            if value is not None:
                return self._loads(value)

            value = self.func(instance)
            safe_write(key, self._dumps(value), self.ttl)
            return value

    def __delete__(self, instance):
        key = self._make_key(instance)
        safe_remove(key)
        
    @staticmethod
    def _dumps(value):
        return orjson.dumps(value).decode()

    @staticmethod
    def _loads(value):
        data = orjson.loads(value)
        try:
            return datetime.fromisoformat(data)
        except (TypeError, ValueError):
            return data

    def _make_key(self, obj):
        return str(self._key(obj, self.func) if callable(self._key) else self._key)


def no_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = cache_disable.set(True)
        try:
            return func(*args, **kwargs)
        finally:
            cache_disable.reset(token)

    return wrapper


def use_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = cache_disable.set(False)
        try:
            return func(*args, **kwargs)
        finally:
            cache_disable.reset(token)

    return wrapper
