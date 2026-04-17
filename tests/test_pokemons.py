"""
tests/test_pokemons.py
----------------------
Testes unitários para as rotas GET /pokemons e GET /pokemons/{name}.

Cada teste valida o *contrato* da rota — o que ela deve fazer —
sem precisar de infraestrutura real (Postgres, Redis, PokéAPI).
"""

import pytest
from unittest.mock import AsyncMock


POKEAPI_LIST_RESPONSE = {
    "count": 1302,
    "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
    "results": [
        {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
        {"name": "pikachu",   "url": "https://pokeapi.co/api/v2/pokemon/25/"},
    ],
}

POKEAPI_DETAIL_RESPONSE = {
    "id": 25,
    "name": "pikachu",
    "types": [{"type": {"name": "electric"}}],
    "stats": [{"base_stat": 35, "stat": {"name": "hp"}}],
}


class TestListPokemons:
    """GET /pokemons"""

    async def test_returns_200_with_pokemon_list(self, client, mock_http_client):
        """Deve retornar 200 com a lista de Pokémons vinda da PokéAPI."""
        mock_http_client.get = AsyncMock(return_value=POKEAPI_LIST_RESPONSE)

        response = await client.get("/pokemons")

        assert response.status_code == 200
        data = response.json()
        # A resposta deve conter pelo menos a lista de resultados da PokéAPI
        assert "results" in data or isinstance(data, list)

    async def test_calls_pokeapi(self, client, mock_http_client):
        """Deve delegar a busca para o http_client (PokéAPI)."""
        mock_http_client.get = AsyncMock(return_value=POKEAPI_LIST_RESPONSE)

        await client.get("/pokemons")

        mock_http_client.get.assert_called_once()

    async def test_does_not_use_database(self, client, mock_http_client, mock_db):
        """Não deve acessar o banco de dados — apenas a API externa."""
        mock_http_client.get = AsyncMock(return_value=POKEAPI_LIST_RESPONSE)

        await client.get("/pokemons")

        mock_db.fetch.assert_not_called()
        mock_db.fetchrow.assert_not_called()


class TestGetPokemon:
    """GET /pokemons/{name}"""

    async def test_returns_cached_pokemon_when_available(
        self, client, mock_cache, mock_http_client
    ):
        """Se o Pokémon estiver no cache, deve retorná-lo sem chamar a PokéAPI."""
        mock_cache.get = AsyncMock(return_value=POKEAPI_DETAIL_RESPONSE)

        response = await client.get("/pokemons/pikachu")

        assert response.status_code == 200
        mock_http_client.get.assert_not_called()

    async def test_fetches_from_pokeapi_when_not_cached(
        self, client, mock_cache, mock_http_client
    ):
        """Se não estiver no cache, deve buscar na PokéAPI."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=POKEAPI_DETAIL_RESPONSE)

        response = await client.get("/pokemons/pikachu")

        assert response.status_code == 200
        mock_http_client.get.assert_called_once()

    async def test_stores_result_in_cache_after_fetch(
        self, client, mock_cache, mock_http_client
    ):
        """Após buscar na PokéAPI, deve salvar o resultado no cache."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(return_value=POKEAPI_DETAIL_RESPONSE)

        await client.get("/pokemons/pikachu")

        mock_cache.set.assert_called_once()

    async def test_returns_404_for_unknown_pokemon(
        self, client, mock_cache, mock_http_client
    ):
        """Deve retornar 404 quando o Pokémon não existir na PokéAPI."""
        import aiohttp

        mock_cache.get = AsyncMock(return_value=None)
        mock_http_client.get = AsyncMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=None, history=(), status=404
            )
        )

        response = await client.get("/pokemons/notapokemon")

        assert response.status_code == 404
