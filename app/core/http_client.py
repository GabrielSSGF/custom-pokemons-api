"""
AiohttpWrapper
--------------
Thin async wrapper around aiohttp.ClientSession.

Usage example
~~~~~~~~~~~~~
    async with AiohttpWrapper(base_url="https://pokeapi.co/api/v2") as client:
        data = await client.get("/pokemon/pikachu")
"""

import aiohttp
from typing import Any


class AiohttpWrapper:
    """Async HTTP client wrapper built on top of aiohttp."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Create the underlying aiohttp session. Call this on app startup."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the underlying aiohttp session. Call this on app shutdown."""
        if self._session and not self._session.closed:
            await self._session.close()

    # Async context-manager support so you can use  `async with AiohttpWrapper() as c:`
    async def __aenter__(self) -> "AiohttpWrapper":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        """Merge base_url with a relative path."""
        return f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Session is not open. Call `await client.start()` first "
                "or use the client as an async context manager."
            )
        return self._session

    # ------------------------------------------------------------------
    # Public HTTP methods  ← alunos NÃO precisam alterar esta classe
    # ------------------------------------------------------------------

    async def get(self, url: str, **kwargs: Any) -> Any:
        """
        Perform an async GET request.

        Parameters
        ----------
        url:
            Relative or absolute URL.
        **kwargs:
            Extra arguments forwarded to ``aiohttp.ClientSession.get``
            (e.g. ``params``, ``headers``).

        Returns
        -------
        Any
            Parsed JSON body.
        """
        session = self._ensure_session()
        async with session.get(self._url(url), **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, url: str, params: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """
        Perform an async POST request.

        Parameters
        ----------
        url:
            Relative or absolute URL.
        params:
            JSON-serialisable body sent as ``json=params``.
        **kwargs:
            Extra arguments forwarded to ``aiohttp.ClientSession.post``.

        Returns
        -------
        Any
            Parsed JSON body.
        """
        session = self._ensure_session()
        async with session.post(self._url(url), json=params, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def patch(self, url: str, params: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """
        Perform an async PATCH request.

        Parameters
        ----------
        url:
            Relative or absolute URL.
        params:
            JSON-serialisable body sent as ``json=params``.
        **kwargs:
            Extra arguments forwarded to ``aiohttp.ClientSession.patch``.

        Returns
        -------
        Any
            Parsed JSON body.
        """
        session = self._ensure_session()
        async with session.patch(self._url(url), json=params, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
