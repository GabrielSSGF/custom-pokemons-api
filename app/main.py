from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.http_client import AiohttpWrapper
from app.core.db import DBManager
from app.core.cache import CacheManager
from app.routers import pokemons, custom_pokemons


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for shared resources."""

    # --- HTTP client ---
    http_client = AiohttpWrapper(base_url=settings.pokeapi_base_url)
    await http_client.start()
    app.state.http_client = http_client

    # --- Postgres ---
    db = DBManager(dsn=settings.asyncpg_dsn)
    await db.connect()
    app.state.db = db

    # --- Redis ---
    cache = CacheManager(url=settings.redis_url, default_ttl=settings.redis_ttl)
    await cache.connect()
    app.state.cache = cache

    yield  # ← application runs here

    # Teardown
    await http_client.close()
    await db.close()
    await cache.close()


app = FastAPI(
    title="Pokémon API",
    description=(
        "Projeto de casa: API assíncrona com FastAPI, asyncpg, Redis e aiohttp. "
        "Os alunos devem implementar os handlers das rotas."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(pokemons.router)
app.include_router(custom_pokemons.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
