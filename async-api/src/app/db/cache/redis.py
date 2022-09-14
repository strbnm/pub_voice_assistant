from typing import Tuple

import ujson
from aioredis import Redis
from app.db.cache.abstract import Cache

from app.core.config import settings


class RedisCache(Cache):
    def __init__(self, cache: Redis):
        self.cache = cache

    async def get(self, key: str):
        data = await self.cache.get(key)
        return ujson.loads(data) if data else data

    async def set(self, key, data: Tuple[list, int]) -> None:
        await self.cache.execute('SET', key, ujson.dumps(data), 'ex', settings.CACHE.TTL)
