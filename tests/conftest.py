"""
conftest.py
-----------
Fixtures compartilhadas para todos os testes.

As dependências (DB, Cache, HTTP client) são substituídas por mocks
para que os testes rodem sem infraestrutura real.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app


# ---------------------------------------------------------------------------
# App state mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_http_client():
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.patch = AsyncMock()
    return client


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.fetch = AsyncMock()
    db.fetchrow = AsyncMock()
    db.execute = AsyncMock()
    db.fetchval = AsyncMock()
    return db


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.exists = AsyncMock(return_value=False)
    return cache


# ---------------------------------------------------------------------------
# Async test client with mocked state
# ---------------------------------------------------------------------------

@pytest.fixture
async def client(mock_http_client, mock_db, mock_cache):
    """
    Async HTTPX client that hits the FastAPI app directly (no real server).
    The app's shared state (http_client, db, cache) is replaced by mocks.
    """
    app.state.http_client = mock_http_client
    app.state.db = mock_db
    app.state.cache = mock_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
