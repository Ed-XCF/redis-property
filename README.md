# redis-property
![GitHub](https://img.shields.io/github/license/Ed-XCF/redis-property)
[![Build Status](https://app.travis-ci.com/Ed-XCF/redis-property.svg?branch=main)](https://app.travis-ci.com/Ed-XCF/redis-property)
[![codecov](https://codecov.io/gh/Ed-XCF/redis-property/branch/main/graph/badge.svg?token=J3HnAigB4J)](undefined)
![PyPI](https://img.shields.io/pypi/v/redis-property)

A decorator for caching properties in redis. Inspired by [cached-property](https://github.com/pydanny/cached-property)

## Installation
```shell
pip3 install redis-property
```

## How to use it

Setup redis_property

```python
import redis_property

redis_property.configure(
    "redis://:123456@example:6379/0", 
    lambda o, f: f"{type(o).__name__}:{o.id}:{f.__name__}"
)
```

use it like python property

```python
from redis_property import redis_property

class Something:
    id = 1
    
    @redis_property(10)  # 24h by default
    def name(self):
        return 1

something = Something()
print(something.name)
```

invalidating the cache

```python
del something.name
```

work with cached-property

```python
from cached_property import cached_property
from redis_property import redis_property

class Something:
    id = 1
    
    @cached_property
    @redis_property
    def name(self):
        return 1
```
