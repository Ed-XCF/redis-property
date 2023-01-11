import random
from datetime import datetime, timedelta
from copy import deepcopy

from cached_property import cached_property

import redis_property as redis_property_lib
from redis_property import redis_property, cache_disable


class TestRedisProperty:
    def setup_class(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            key_maker=lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}",
            disable=False,
        )

    def test_work_alone(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @redis_property
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number == adder.number
        del adder.number
        assert adder.number == 3
        del adder.number

    def test_work_alone_with_ttl(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @redis_property(1)
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number == adder.number
        del adder.number
        assert adder.number == 3
        del adder.number

    def test_work_with_cached_property(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @cached_property
            @redis_property(1)
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number == adder.number


class TestRedisPropertyWithContextVar:
    def setup_class(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            key_maker=lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}",
            disable=False,
        )

    def test_work_with_cache_disable(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @redis_property
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number == adder.number
        del adder.number
        assert adder.number == 3
        del adder.number

        cache_disable.set(True)
        assert adder.number != adder.number
        del adder.number
        assert adder.number == 6
        del adder.number

        cache_disable.set(False)
        assert adder.number == adder.number
        del adder.number
        assert adder.number == 8
        del adder.number


class TestDisabledRedisProperty:
    def setup_class(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            key_maker=lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}",
            disable=True,
        )

    def test_work_alone(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @redis_property
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number != adder.number
        del adder.number
        assert adder.number == 4
        del adder.number

    def test_work_alone_with_ttl(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @redis_property(1)
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number != adder.number
        del adder.number
        assert adder.number == 4
        del adder.number

    def test_work_with_cached_property(self):
        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.times = 1

            @cached_property
            @redis_property(1)
            def number(self):
                self.times += 1
                return self.times

        adder = Adder()
        assert adder.number == adder.number


class TestRedisPropertyDatetime:
    def setup_class(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            key_maker=lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}",
            disable=False,
        )
        print(cache_disable.get())

    def test_work_for_datetime(self):
        now = datetime.now()

        class Adder:
            id = random.randint(1, 1000)

            def __init__(self):
                self.now = deepcopy(now)

            @redis_property
            def current(self):
                self.now += timedelta(seconds=1)
                return self.now

        adder = Adder()
        assert adder.current == adder.current
        del adder.current
        assert adder.current == now + timedelta(seconds=2)
        del adder.current

        cache_disable.set(True)
        assert adder.current != adder.current
        del adder.current
        assert adder.current == now + timedelta(seconds=5)
        del adder.current

        cache_disable.set(False)
        assert adder.current == adder.current
        del adder.current
        assert adder.current == now + timedelta(seconds=7)
        del adder.current
