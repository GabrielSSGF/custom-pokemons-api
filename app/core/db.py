"""
DBManager
---------
Async Postgres manager built on top of asyncpg connection pools.

Schema example (run this SQL once to bootstrap your database)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CREATE TABLE IF NOT EXISTS custom_pokemons (
        id          SERIAL PRIMARY KEY,
        name        VARCHAR(100) UNIQUE NOT NULL,
        type        VARCHAR(50)  NOT NULL,
        hp          INTEGER      NOT NULL DEFAULT 0,
        attack      INTEGER      NOT NULL DEFAULT 0,
        defense     INTEGER      NOT NULL DEFAULT 0,
        created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    );

Usage example
~~~~~~~~~~~~~
    db = DBManager(dsn="postgresql://user:pass@localhost/mydb")
    await db.connect()

    row = await db.fetchrow("SELECT * FROM custom_pokemons WHERE name = $1", "bulbasaur")
    await db.close()
"""

import asyncpg
from typing import Any


class DBManager:
    """Async Postgres manager using an asyncpg connection pool."""

    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 10) -> None:
        """
        Parameters
        ----------
        dsn:
            PostgreSQL connection string.
            Example: ``postgresql://user:password@localhost:5432/mydb``
        min_size:
            Minimum number of connections kept in the pool.
        max_size:
            Maximum number of connections allowed in the pool.
        """
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    # ------------------------------------------------------------------
    # Pool lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Open the connection pool. Call this on application startup."""
        self._pool = await asyncpg.create_pool(
            dsn=self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
        )

    async def close(self) -> None:
        """Close all connections in the pool. Call this on application shutdown."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    def _ensure_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError(
                "Database pool is not initialised. Call `await db.connect()` first."
            )
        return self._pool

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    async def execute(self, query: str, *args: Any) -> str:
        """
        Execute a DML statement (INSERT / UPDATE / DELETE) and return the
        status string returned by Postgres (e.g. ``"INSERT 0 1"``).
        """
        pool = self._ensure_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """
        Fetch at most one row.

        Returns ``None`` when no row matches.
        """
        pool = self._ensure_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """Fetch all matching rows as a list of :class:`asyncpg.Record`."""
        pool = self._ensure_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchval(self, query: str, *args: Any, column: int = 0) -> Any:
        """Fetch a single value from the first row of the result."""
        pool = self._ensure_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args, column=column)

    # ------------------------------------------------------------------
    # Schema bootstrap helper (optional, for development convenience)
    # ------------------------------------------------------------------

    async def create_tables(self) -> None:
        """
        Create application tables if they do not exist yet.

        TODO (alunos): adicione suas instruções CREATE TABLE aqui.

        Exemplo:
            await self.execute(
                \"\"\"
                CREATE TABLE IF NOT EXISTS custom_pokemons (
                    id         SERIAL PRIMARY KEY,
                    name       VARCHAR(100) UNIQUE NOT NULL,
                    type       VARCHAR(50)  NOT NULL,
                    hp         INTEGER      NOT NULL DEFAULT 0,
                    attack     INTEGER      NOT NULL DEFAULT 0,
                    defense    INTEGER      NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
                );
                \"\"\"
            )
        """
        # TODO: implemente a criação das tabelas aqui
        raise NotImplementedError("Implemente create_tables() com seus CREATE TABLE statements.")
