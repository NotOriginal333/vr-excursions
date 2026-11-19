import json
from collections.abc import Awaitable, Callable
from typing import Any


async def cached(client, key: str, ttl_seconds: int, produce: Callable[[], Awaitable[Any]]) -> Any:
    if (hit := await client.get(key)) is not None:
        return json.loads(hit)
    value = await produce()
    await client.set(key, json.dumps(value), ex=ttl_seconds)
    return value
