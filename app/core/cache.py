"""
CacheManager
------------
Thin async wrapper around the redis-py async client.

Usage example
~~~~~~~~~~~~~
    cache = CacheManager(url="redis://localhost:6379", default_ttl=300)
    await cache.connect()

    await cache.set("pokemon:pikachu", '{"name": "pikachu", ...}')
    value = await cache.get("pokemon:pikachu")
    await cache.delete("pokemon:pikachu")

    await cache.close()
"""

import json
from typing import Any

import redis.asyncio as aioredis


class CacheManager:
    """Async Redis cache manager."""

    def __init__(self, url: str, default_ttl: int = 300) -> None:
        """
        Parameters
        ----------
        url:
            Redis connection URL. Example: ``redis://localhost:6379``
        default_ttl:
            Default time-to-live in seconds for cached entries.
        """
        self._url = url
        self.default_ttl = default_ttl
        self._client: aioredis.Redis | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Open the Redis connection. Call this on application startup."""
        self._client = aioredis.from_url(self._url, decode_responses=True)

    async def close(self) -> None:
        """Close the Redis connection. Call this on application shutdown."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError(
                "Redis client is not initialised. Call `await cache.connect()` first."
            )
        return self._client

    # ------------------------------------------------------------------
    # Cache operations
    # ------------------------------------------------------------------

    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value by key.

        Returns the deserialised Python object or ``None`` when the key
        does not exist or has expired.
        """
        client = self._ensure_client()
        raw = await client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Store *value* under *key* with an optional TTL.

        Parameters
        ----------
        key:
            Cache key.
        value:
            Any JSON-serialisable object (or a plain string).
        ttl:
            Time-to-live in seconds. Falls back to ``self.default_ttl``.
        """
        client = self._ensure_client()
        serialised = json.dumps(value) if not isinstance(value, str) else value
        await client.set(key, serialised, ex=ttl or self.default_ttl)

    async def delete(self, key: str) -> None:
        """Remove *key* from the cache (no-op if it doesn't exist)."""
        client = self._ensure_client()
        await client.delete(key)

    async def exists(self, key: str) -> bool:
        """Return ``True`` if *key* exists in the cache."""
        client = self._ensure_client()
        return bool(await client.exists(key))
