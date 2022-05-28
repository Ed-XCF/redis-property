import random

import redis_property as redis_property_lib
from redis_property import redis_property

redis_property_lib.configure(
    "redis://:@127.0.0.1:6379/0",
    lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}"
)


def test_redis_property():
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
