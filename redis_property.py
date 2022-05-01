import json
from threading import RLock

from redis import Redis, RedisError

__all__ = ["redis_property"]

_redis_cli = None
_default_ttl = 24 * 60 * 60


def _default_key(obj, func):
    return type(obj).__name__ + func.__name__


def configure(url, default_key=None, default_ttl=_default_ttl):
    global _redis_cli
    _redis_cli = Redis.from_url(url)

    global _default_ttl
    _default_ttl = default_ttl

    if default_key is not None:
        global _default_key  # noqa
        _default_key = default_key


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

        return value.decode("utf-8")


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
            self.func, self.ttl = seconds, _default_ttl
        else:
            self.func, self.ttl = None, seconds

        self._key = key or _default_key
        self._copy_func_info()
        self.lock = RLock()

    def __call__(self, func):
        if self.func is not None:
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

    _dumps = staticmethod(json.dumps)
    _loads = staticmethod(json.loads)

    def _make_key(self, obj):
        return str(self._key(obj, self.func) if callable(self._key) else self._key)
