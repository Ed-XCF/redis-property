import random

from cached_property import cached_property

import redis_property as redis_property_lib
from redis_property import redis_property


class TestRedisProperty:
    def setUp(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}"
        )

    def test_work_alone(self):
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


class TestDisabledRedisProperty:
    def setUp(self):
        redis_property_lib.configure(
            "redis://:@127.0.0.1:6379/0",
            lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}",
            disable=True,
        )

    def test_work_alone(self):
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
